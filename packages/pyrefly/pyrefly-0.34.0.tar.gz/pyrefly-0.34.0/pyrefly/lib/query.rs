/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//! Query interface for pyrefly. Just experimenting for the moment - not intended for external use.

use std::io::Cursor;
use std::iter;
use std::path::PathBuf;
use std::sync::Arc;

use dupe::Dupe;
use itertools::Itertools;
use pyrefly_build::handle::Handle;
use pyrefly_python::ast::Ast;
use pyrefly_python::dunder;
use pyrefly_python::module_name::ModuleName;
use pyrefly_python::module_path::ModulePath;
use pyrefly_python::qname::QName;
use pyrefly_python::short_identifier::ShortIdentifier;
use pyrefly_python::sys_info::SysInfo;
use pyrefly_types::callable::FuncMetadata;
use pyrefly_types::callable::Function;
use pyrefly_types::callable::FunctionKind;
use pyrefly_types::class::Class;
use pyrefly_types::literal::Lit;
use pyrefly_types::quantified::Quantified;
use pyrefly_types::quantified::QuantifiedKind;
use pyrefly_types::type_var::Restriction;
use pyrefly_types::types::BoundMethodType;
use pyrefly_types::types::Forallable;
use pyrefly_types::types::Type;
use pyrefly_util::events::CategorizedEvents;
use pyrefly_util::lined_buffer::DisplayRange;
use pyrefly_util::lock::Mutex;
use pyrefly_util::prelude::SliceExt;
use pyrefly_util::prelude::VecExt;
use pyrefly_util::visit::Visit;
use ruff_python_ast::Arguments;
use ruff_python_ast::Decorator;
use ruff_python_ast::Expr;
use ruff_python_ast::ExprAttribute;
use ruff_python_ast::ExprName;
use ruff_python_ast::ModModule;
use ruff_python_ast::Stmt;
use ruff_python_ast::StmtClassDef;
use ruff_python_ast::StmtFunctionDef;
use ruff_python_ast::name::Name;
use ruff_text_size::Ranged;
use ruff_text_size::TextRange;
use ruff_text_size::TextSize;
use starlark_map::small_set::SmallSet;

use crate::alt::answers::Answers;
use crate::alt::answers_solver::AnswersSolver;
use crate::binding::binding::Key;
use crate::binding::binding::KeyClassSynthesizedFields;
use crate::binding::bindings::Bindings;
use crate::config::finder::ConfigFinder;
use crate::module::module_info::ModuleInfo;
use crate::state::lsp::DefinitionMetadata;
use crate::state::lsp::FindPreference;
use crate::state::require::Require;
use crate::state::state::State;
use crate::state::state::Transaction;
use crate::state::state::TransactionHandle;
use crate::types::display::TypeDisplayContext;

const REPR: Name = Name::new_static("__repr__");

pub struct Query {
    /// The state that we use.
    state: State,
    /// The SysInfo, the same for all handles.
    sys_info: SysInfo,
    /// The files that have been used with `add_files`, used when files change.
    files: Mutex<SmallSet<(ModuleName, ModulePath)>>,
}

const CALLEE_KIND_FUNCTION: &str = "function";
const CALLEE_KIND_METHOD: &str = "method";
const CALLEE_KIND_CLASSMETHOD: &str = "classmethod";
const CALLEE_KIND_STATICMETHOD: &str = "staticmethod";

#[derive(Hash, Eq, PartialEq, Clone, Debug)]
pub struct Callee {
    /// What kind of callable is this? Distinguishes various kinds of methods from normal functions.
    pub kind: String,
    /// What's the qualified name of the callable. The name `target` is for Pyre compatibility and originates in Pysa vocabulary.
    pub target: String,
    /// If this is a method, what class is it defined on?
    pub class_name: Option<String>,
}

pub struct Attribute {
    pub name: String,
    pub kind: Option<String>,
    pub annotation: String,
}

fn display_range_for_expr(
    module_info: &ModuleInfo,
    original_range: TextRange,
    expr: &Expr,
    parent_expr: Option<&Expr>,
) -> DisplayRange {
    let expression_range = if let Expr::Generator(e) = expr {
        // python AST module reports locations of all generator expressions as if they are parenthesized
        // i.e any(any(a.b is not None for a in [l2]) for l2 in l1)
        //        ^-will be col_offset for generator expression over l1
        // ruff properly distinguishes between parenthesized and non-parenthesized expressions
        // and points to the first character of the expression
        // since queries are done based on Python AST for generator expression we will
        // need to adjust start/end column offsets
        if e.parenthesized {
            original_range
        } else if let Some(Expr::Call(p)) = parent_expr
            && p.arguments.len() == 1
            && p.arguments.inner_range().contains_range(original_range)
        {
            TextRange::new(
                p.arguments.l_paren_range().start(),
                p.arguments.r_paren_range().end(),
            )
        } else {
            original_range
                .sub_start(TextSize::new(1))
                .add_end(TextSize::new(1))
        }
    } else {
        original_range
    };
    module_info.display_range(expression_range)
}

fn is_static_method(ty: &Type) -> bool {
    match ty {
        Type::Union(tys) => tys.iter().all(is_static_method),
        Type::BoundMethod(m) => m.func.metadata().flags.is_staticmethod,
        Type::Function(f) => f.metadata.flags.is_staticmethod,
        Type::Forall(f) => {
            if let Forallable::Function(func) = &f.body {
                func.metadata.flags.is_staticmethod
            } else {
                false
            }
        }
        _ => false,
    }
}

fn bound_of_type_var(ty: &Type) -> Option<&Type> {
    match ty {
        Type::Quantified(box Quantified {
            kind: QuantifiedKind::TypeVar,
            restriction: Restriction::Bound(bound),
            ..
        })
        | Type::QuantifiedValue(box Quantified {
            kind: QuantifiedKind::TypeVar,
            restriction: Restriction::Bound(bound),
            ..
        }) => Some(bound),
        _ => None,
    }
}

fn bound_of_type_var_decl(ty: &Type) -> Option<(&QName, &Type)> {
    if let Type::TypeVar(tv) = ty
        && let Restriction::Bound(bound) = tv.restriction()
    {
        Some((tv.qname(), bound))
    } else {
        None
    }
}

fn type_to_string(ty: &Type) -> String {
    let mut ctx = TypeDisplayContext::new(&[ty]);
    ctx.always_display_module_name();
    if is_static_method(ty) {
        format!("typing.StaticMethod[{}]", ctx.display(ty))
    } else if let Some(bound) = bound_of_type_var(ty) {
        // pyre1 compatibility: return bound for type variable
        format!(
            "Variable[{} (bound to {})]",
            ctx.display(ty),
            type_to_string(bound)
        )
    } else if let Some((qname, bound)) = bound_of_type_var_decl(ty) {
        // pyre1 compatibility: return bound for type variable
        format!(
            "Variable[{} (bound to {})]",
            qname.id(),
            type_to_string(bound)
        )
    } else {
        ctx.display(ty).to_string()
    }
}

impl Query {
    pub fn new(config_finder: ConfigFinder) -> Self {
        let state = State::new(config_finder);
        Self {
            state,
            sys_info: SysInfo::default(),
            files: Mutex::new(SmallSet::new()),
        }
    }

    fn make_handle(&self, name: ModuleName, path: ModulePath) -> Handle {
        let config = self.state.config_finder().python_file(name.dupe(), &path);
        if config.source_db.read().is_some() {
            panic!("Pyrefly doesn't support sourcedb-powered queries yet");
        }
        // TODO(connernilsen): make this work with build systems
        Handle::new(name, path, self.sys_info.dupe())
    }

    pub fn change_files(&self, events: &CategorizedEvents) {
        let mut transaction = self
            .state
            .new_committable_transaction(Require::Everything, None);
        let new_transaction_mut = transaction.as_mut();
        new_transaction_mut.invalidate_events(events);
        new_transaction_mut.run(&[], Require::Everything);
        self.state.commit_transaction(transaction);
        let all_files = self.files.lock().iter().cloned().collect::<Vec<_>>();
        self.add_files(all_files);
    }

    pub fn change(&self, files: Vec<(ModuleName, std::path::PathBuf)>) {
        let modified_paths = files.into_iter().map(|(_, path)| path).collect();
        let events = CategorizedEvents {
            created: Vec::new(),
            modified: modified_paths,
            removed: Vec::new(),
            unknown: Vec::new(),
        };
        self.change_files(&events);
    }

    /// Load the given files and return any errors associated with them
    pub fn add_files(&self, files: Vec<(ModuleName, ModulePath)>) -> Vec<String> {
        self.files.lock().extend(files.iter().cloned());
        let mut transaction = self
            .state
            .new_committable_transaction(Require::Exports, None);
        let handles = files.into_map(|(name, file)| self.make_handle(name, file));
        transaction.as_mut().run(&handles, Require::Everything);
        let errors = transaction.as_mut().get_errors(&handles);
        self.state.commit_transaction(transaction);
        let project_root = PathBuf::new();
        errors.collect_errors().shown.map(|e| {
            // We deliberately don't have a Display for `Error`, to encourage doing the right thing.
            // But we just hack something up as this code is experimental.
            let mut s = Cursor::new(Vec::new());
            e.write_line(&mut s, project_root.as_path(), false).unwrap();
            String::from_utf8_lossy(&s.into_inner()).into_owned()
        })
    }

    pub fn get_attributes(
        &self,
        name: ModuleName,
        path: ModulePath,
        class_name: &str,
    ) -> Option<Vec<Attribute>> {
        let transaction = self.state.transaction();
        let handle = self.make_handle(name, path);
        let ast = transaction.get_ast(&handle)?;
        // find last declaration of class with specified name in file
        let cls = ast
            .body
            .iter()
            .filter_map(|e| {
                if let Stmt::ClassDef(cls) = e {
                    if cls.name.id.as_str() == class_name {
                        Some(cls)
                    } else {
                        None
                    }
                } else {
                    None
                }
            })
            .last()?;
        let class_ty = transaction.get_type_at(&handle, cls.name.start());
        fn get_kind_and_field_type(ty: &Type) -> (Option<String>, &Type) {
            match ty {
                Type::Function(f) if f.metadata.flags.is_property_getter => {
                    (Some(String::from("property")), ty)
                }
                Type::ClassType(c) if c.name() == "classproperty" => {
                    let result_ty = c.targs().as_slice().get(1).unwrap();
                    (Some(String::from("property")), result_ty)
                }
                _ => (None, ty),
            }
        }
        if let Some(Type::ClassDef(cd)) = &class_ty {
            let res = cd
                .fields()
                .filter_map(|n| {
                    let range = cd.field_decl_range(n)?;
                    let field_ty = transaction.get_type_at(&handle, range.start())?;
                    let (kind, field_ty) = get_kind_and_field_type(&field_ty);
                    Some(Attribute {
                        name: n.to_string(),
                        kind,
                        annotation: type_to_string(field_ty),
                    })
                })
                .collect_vec();
            Some(res)
        } else {
            None
        }
    }

    // fetches information about callees of a callable in a module
    pub fn get_callees_with_location(
        &self,
        name: ModuleName,
        path: ModulePath,
    ) -> Option<Vec<(DisplayRange, Callee)>> {
        let transaction = self.state.transaction();
        let handle = self.make_handle(name, path);
        let module_info = transaction.get_module_info(&handle)?;
        let ast = transaction.get_ast(&handle)?;
        let answers = transaction.get_answers(&handle)?;

        fn qname_to_string(n: &QName) -> String {
            format!("{}.{}", n.module_name(), n.id())
        }
        fn class_name_from_def_kind(kind: &FunctionKind) -> String {
            if let FunctionKind::Def(f) = kind
                && let Some(class_name) = &f.cls
            {
                format!("{}.{}", f.module, class_name)
            } else {
                panic!("class_name_from_def_kind - unsupported function kind: {kind:?}");
            }
        }
        fn target_from_def_kind(kind: &FunctionKind, module_name_override: Option<&str>) -> String {
            match kind {
                FunctionKind::Def(f) => {
                    if let Some(module_name_override) = module_name_override {
                        format!("{module_name_override}.{}", f.func)
                    } else {
                        match &f.cls {
                            Some(class_name) => {
                                format!("{}.{}.{}", f.module, class_name, f.func)
                            }
                            None => {
                                format!("{}.{}", f.module, f.func)
                            }
                        }
                    }
                }
                FunctionKind::CallbackProtocol(cls) => {
                    format!("{}.__call__", qname_to_string(cls.qname()))
                }

                x => x.as_func_id().format(ModuleName::builtins()),
            }
        }
        fn repr_from_arguments(
            arguments: &Arguments,
            answers: &Answers,
            transaction: &Transaction<'_>,
            handle: &Handle,
        ) -> Option<Callee> {
            // Use the type of the first argument to find the callee.
            if let Some(arg_type) = answers.get_type_trace(arguments.args[0].range())
                && let Type::ClassType(class) = &arg_type
            {
                let repr_callees = callee_from_mro(
                    class.class_object(),
                    transaction,
                    handle,
                    "__repr__",
                    |_solver, c| {
                        if c.contains(&REPR) {
                            Some(format!("{}.{}.__repr__", c.module_name(), c.name()))
                        } else {
                            None
                        }
                    },
                );
                if !repr_callees.is_empty() {
                    return Some(repr_callees[0].clone());
                }
            }
            None
        }
        fn callee_from_function(
            f: &Function,
            call_target: Option<&Expr>,
            call_arguments: Option<&Arguments>,
            answers: &Answers,
            transaction: &Transaction<'_>,
            handle: &Handle,
        ) -> Callee {
            if f.metadata.flags.is_staticmethod {
                Callee {
                    kind: String::from(CALLEE_KIND_STATICMETHOD),
                    target: target_from_def_kind(&f.metadata.kind, None),
                    class_name: Some(class_name_from_def_kind(&f.metadata.kind)),
                }
            } else if f.metadata.flags.is_classmethod {
                Callee {
                    kind: String::from(CALLEE_KIND_CLASSMETHOD),
                    target: target_from_def_kind(&f.metadata.kind, None),
                    // TODO: use type of receiver
                    class_name: Some(class_name_from_def_kind(&f.metadata.kind)),
                }
            } else {
                // Check if this is a builtins function that needs special casing.
                if let FunctionKind::Def(def) = &f.metadata.kind
                    && def.module.as_str() == "builtins"
                    && def.func == "repr"
                    && let Some(args) = call_arguments
                    && let Some(callee) = repr_from_arguments(args, answers, transaction, handle)
                {
                    return callee;
                }

                let class_name = class_name_from_call_target(call_target, answers);
                let kind = if class_name.is_some() {
                    String::from(CALLEE_KIND_METHOD)
                } else {
                    String::from(CALLEE_KIND_FUNCTION)
                };

                Callee {
                    kind,
                    target: target_from_def_kind(&f.metadata.kind, None),
                    class_name,
                }
            }
        }
        fn target_from_bound_method_type(
            m: &BoundMethodType,
            method_of_typed_dict: bool,
        ) -> String {
            let module_name_override = if method_of_typed_dict {
                Some("TypedDictionary")
            } else {
                None
            };
            match m {
                BoundMethodType::Function(f) => {
                    target_from_def_kind(&f.metadata.kind, module_name_override)
                }
                BoundMethodType::Forall(f) => {
                    target_from_def_kind(&f.body.metadata.kind, module_name_override)
                }
                BoundMethodType::Overload(f) => {
                    target_from_def_kind(&f.metadata.kind, module_name_override)
                }
            }
        }
        fn callee_method_kind_from_function_metadata(m: &FuncMetadata) -> String {
            if m.flags.is_staticmethod {
                String::from(CALLEE_KIND_STATICMETHOD)
            } else if m.flags.is_classmethod {
                String::from(CALLEE_KIND_CLASSMETHOD)
            } else {
                String::from(CALLEE_KIND_METHOD)
            }
        }
        fn callee_method_kind_from_bound_method_type(m: &BoundMethodType) -> String {
            match m {
                BoundMethodType::Function(f) => {
                    callee_method_kind_from_function_metadata(&f.metadata)
                }
                BoundMethodType::Forall(f) => {
                    callee_method_kind_from_function_metadata(&f.body.metadata)
                }
                BoundMethodType::Overload(f) => {
                    callee_method_kind_from_function_metadata(&f.metadata)
                }
            }
        }
        fn class_info_for_qname(qname: &QName, is_typed_dict: bool) -> Vec<(String, bool)> {
            vec![(qname_to_string(qname), is_typed_dict)]
        }
        fn class_info_from_bound_obj(ty: &Type) -> Vec<(String, bool)> {
            match ty {
                Type::SelfType(c) => class_info_for_qname(c.qname(), false),
                // TODO: wrap in 'type'
                Type::Type(t) => class_info_from_bound_obj(t),
                Type::ClassType(c) => class_info_for_qname(c.qname(), false),
                Type::ClassDef(c) => class_info_for_qname(c.qname(), false),
                Type::TypedDict(d) => class_info_for_qname(d.qname(), true),
                Type::Literal(Lit::Str(_)) | Type::LiteralString => {
                    vec![(String::from("builtins.str"), false)]
                }
                Type::Literal(Lit::Int(_)) => vec![(String::from("builtins.int"), false)],
                Type::Literal(Lit::Bool(_)) => vec![(String::from("builtins.bool"), false)],
                Type::Quantified(q) => match &q.restriction {
                    // for explicit bound - use name of the type used as bound
                    Restriction::Bound(b) => class_info_from_bound_obj(b),
                    // no bound - use name of the type variable (not very useful but not worse than status quo)
                    Restriction::Unrestricted => vec![(q.name().to_string(), false)],
                    Restriction::Constraints(_) => {
                        panic!("unexpected restriction: {q:?}")
                    }
                },
                Type::Union(tys) => tys.iter().flat_map(class_info_from_bound_obj).collect_vec(),
                _ => panic!("unexpected type: {ty:?}"),
            }
        }
        fn callee_from_mro<F: Fn(&AnswersSolver<TransactionHandle>, &Class) -> Option<String>>(
            c: &Class,
            transaction: &Transaction<'_>,
            handle: &Handle,
            fallback_name: &str,
            callee_from_ancestor: F,
        ) -> Vec<Callee> {
            let call_target = transaction.ad_hoc_solve(handle, |solver| {
                let mro = solver.get_mro_for_class(c);
                iter::once(c)
                    .chain(mro.ancestors(solver.stdlib).map(|x| x.class_object()))
                    .find_map(|c| callee_from_ancestor(&solver, c))
            });
            let class_name = qname_to_string(c.qname());
            let target = if let Some(Some(t)) = call_target {
                t
            } else {
                format!("{class_name}.{fallback_name}")
            };
            vec![Callee {
                kind: String::from(CALLEE_KIND_METHOD),
                target,
                class_name: Some(class_name),
            }]
        }
        fn for_callable(
            callee_range: TextRange,
            module_info: &ModuleInfo,
            transaction: &Transaction<'_>,
            handle: &Handle,
        ) -> Vec<Callee> {
            // a bit unfortunate that we have to rely on LSP functionality to get the target
            let defs = transaction
                .find_definition(
                    handle,
                    // take location of last included character in range (which should work for identifiers and attributes)
                    callee_range.end().checked_sub(TextSize::from(1)).unwrap(),
                    &FindPreference::default(),
                )
                .into_iter()
                // filter out attributes since we don't know how to handle them
                .filter(|d| !matches!(d.metadata, DefinitionMetadata::Attribute(_)))
                .collect_vec();
            if defs.is_empty() {
                vec![]
            } else if defs.len() == 1 {
                // TODO: decide what do to with multiple definitions
                let def0 = &defs[0];
                if def0.module.name() == handle.module() {
                    match &def0.metadata {
                        DefinitionMetadata::Variable(_) => {
                            let name = module_info.code_at(defs[0].definition_range);
                            vec![Callee {
                                kind: String::from(CALLEE_KIND_FUNCTION),
                                target: format!("$parameter${name}"),
                                class_name: None,
                            }]
                        }
                        x => panic!("callable ty - unexpected metadata kind, {x:?}"),
                    }
                } else {
                    vec![]
                }
            } else {
                panic!(
                    "callable ty at [{}] not supported yet, {defs:?}",
                    module_info.display_range(callee_range)
                )
            }
        }
        fn class_name_from_call_target(
            call_target: Option<&Expr>,
            answers: &Answers,
        ) -> Option<String> {
            if let Some(Expr::Attribute(attr)) = call_target
                && let Some(ty) = answers.get_type_trace(attr.value.range())
                && !matches!(ty, Type::Module(_))
            {
                // treat calls where targets are attribute access a.b and a is not a module
                // as method calls
                Some(type_to_string(&ty))
            } else {
                None
            }
        }

        fn find_init_or_new(
            cls: &Class,
            transaction: &Transaction<'_>,
            handle: &Handle,
        ) -> Vec<Callee> {
            callee_from_mro(cls, transaction, handle, "__init__", |solver, c| {
                // find first class that has __init__ or __new__
                let has_init = c.contains(&dunder::INIT)
                    || solver
                        .get_from_class(c, &KeyClassSynthesizedFields(c.index()))
                        .is_some_and(|f| f.get(&dunder::INIT).is_some());
                if has_init {
                    Some(format!("{}.{}.__init__", c.module_name(), c.name()))
                } else if c.contains(&dunder::NEW) {
                    Some(format!("{}.{}.__new__", c.module_name(), c.name()))
                } else {
                    None
                }
            })
        }
        fn init_or_new_from_type(
            ty: &Type,
            callee_range: TextRange,
            transaction: &Transaction<'_>,
            handle: &Handle,
            module_info: &ModuleInfo,
        ) -> Vec<Callee> {
            match ty {
                Type::SelfType(c) | Type::ClassType(c) => {
                    find_init_or_new(c.class_object(), transaction, handle)
                }
                Type::Quantified(box q) => match &q.restriction {
                    Restriction::Bound(Type::ClassType(c)) => {
                        find_init_or_new(c.class_object(), transaction, handle)
                    }
                    x => panic!(
                        "unexpected restriction {}: {x:?}",
                        module_info.display_range(callee_range)
                    ),
                },
                Type::Union(tys) => {
                    // get callee for each type
                    tys.iter()
                        .flat_map(|t| {
                            init_or_new_from_type(t, callee_range, transaction, handle, module_info)
                        })
                        .unique()
                        // return sorted by target
                        .sorted_by(|a, b| a.target.cmp(&b.target))
                        .collect_vec()
                }
                x => {
                    panic!(
                        "unexpected type at [{}]: {x:?}",
                        module_info.display_range(callee_range)
                    );
                }
            }
        }
        fn callee_from_type(
            ty: &Type,
            call_target: Option<&Expr>,
            callee_range: TextRange,
            call_arguments: Option<&Arguments>,
            module_info: &ModuleInfo,
            transaction: &Transaction<'_>,
            handle: &Handle,
            answers: &Answers,
        ) -> Vec<Callee> {
            match ty {
                Type::Quantified(q) => match &q.restriction {
                    Restriction::Bound(b) => callee_from_type(
                        b,
                        call_target,
                        callee_range,
                        call_arguments,
                        module_info,
                        transaction,
                        handle,
                        answers,
                    ),
                    x => panic!(
                        "unexpected restriction {}: {x:?}",
                        module_info.display_range(callee_range)
                    ),
                },
                Type::Never(_) => vec![],
                Type::Union(tys) => {
                    // get callee for each type
                    tys.iter()
                        .flat_map(|t| {
                            callee_from_type(
                                t,
                                call_target,
                                callee_range,
                                call_arguments,
                                module_info,
                                transaction,
                                handle,
                                answers,
                            )
                        })
                        .unique()
                        // return sorted by target
                        .sorted_by(|a, b| a.target.cmp(&b.target))
                        .collect_vec()
                }
                Type::BoundMethod(m) => class_info_from_bound_obj(&m.obj)
                    .into_iter()
                    .map(|(class_name, class_is_typed_dict)| Callee {
                        kind: callee_method_kind_from_bound_method_type(&m.func),
                        target: target_from_bound_method_type(&m.func, class_is_typed_dict),
                        class_name: Some(class_name),
                    })
                    .unique()
                    // return sorted by target
                    .sorted_by(|a, b| a.target.cmp(&b.target))
                    .collect_vec(),

                Type::Function(f) => {
                    vec![callee_from_function(
                        f,
                        call_target,
                        call_arguments,
                        answers,
                        transaction,
                        handle,
                    )]
                }
                Type::Overload(f) => {
                    let class_name = class_name_from_call_target(call_target, answers);
                    let kind = if class_name.is_some() {
                        String::from(CALLEE_KIND_METHOD)
                    } else {
                        String::from(CALLEE_KIND_FUNCTION)
                    };
                    // assuming that overload represents function and method overloads
                    // are handled by BoundMethod case
                    vec![Callee {
                        kind,
                        target: target_from_def_kind(&f.metadata.kind, None),
                        class_name,
                    }]
                }
                Type::Callable(..) => for_callable(callee_range, module_info, transaction, handle),
                Type::Type(box ty) => {
                    init_or_new_from_type(ty, callee_range, transaction, handle, module_info)
                }

                Type::ClassDef(cls) => find_init_or_new(cls, transaction, handle),
                Type::Forall(v) => match &v.body {
                    Forallable::Function(func) => {
                        vec![callee_from_function(
                            func,
                            call_target,
                            call_arguments,
                            answers,
                            transaction,
                            handle,
                        )]
                    }
                    Forallable::Callable(_) => {
                        for_callable(callee_range, module_info, transaction, handle)
                    }
                    Forallable::TypeAlias(t) => callee_from_type(
                        &t.as_type(),
                        call_target,
                        callee_range,
                        call_arguments,
                        module_info,
                        transaction,
                        handle,
                        answers,
                    ),
                },
                Type::SelfType(c) | Type::ClassType(c) => callee_from_mro(
                    c.class_object(),
                    transaction,
                    handle,
                    "__call__",
                    |_solver, c| {
                        if c.contains(&dunder::CALL) {
                            Some(format!("{}.{}.__call__", c.module_name(), c.name()))
                        } else {
                            None
                        }
                    },
                ),
                Type::Any(_) => vec![],
                Type::TypeAlias(t) => callee_from_type(
                    &t.as_type(),
                    call_target,
                    callee_range,
                    call_arguments,
                    module_info,
                    transaction,
                    handle,
                    answers,
                ),
                _ => panic!(
                    "unexpected type at [{}]: {ty:?}",
                    module_info.display_range(callee_range)
                ),
            }
        }

        let mut res = Vec::new();
        fn process_expr<'a>(
            x: &Expr,
            module_info: &ModuleInfo,
            answers: &Answers,
            transaction: &Transaction<'a>,
            handle: &Handle,
            res: &mut Vec<(DisplayRange, Callee)>,
        ) {
            let (callee_ty, callee_range, call_target, call_arguments) =
                if let Expr::Attribute(attr) = x {
                    (
                        answers.try_get_getter_for_range(attr.range()),
                        attr.range(),
                        None,
                        None,
                    )
                } else if let Expr::Call(call) = x {
                    (
                        answers.get_type_trace(call.func.range()),
                        call.func.range(),
                        Some(&*call.func),
                        Some(&call.arguments),
                    )
                } else {
                    (None, x.range(), None, None)
                };
            if let Some(func_ty) = callee_ty {
                callee_from_type(
                    &func_ty,
                    call_target,
                    callee_range,
                    call_arguments,
                    module_info,
                    transaction,
                    handle,
                    answers,
                )
                .into_iter()
                .for_each(|callee| {
                    res.push((module_info.display_range(callee_range), callee));
                });
            }

            x.recurse(&mut |x| process_expr(x, module_info, answers, transaction, handle, res));
        }

        fn add_decorators<'a>(
            decorators: &[Decorator],
            module_info: &ModuleInfo,
            answers: &Answers,
            transaction: &Transaction<'a>,
            handle: &Handle,
            res: &mut Vec<(DisplayRange, Callee)>,
        ) {
            for dec in decorators {
                if matches!(dec.expression, Expr::Name(_) | Expr::Attribute(_))
                    && let Some(call_ty) = answers.get_type_trace(dec.expression.range())
                {
                    callee_from_type(
                        &call_ty,
                        None,
                        dec.expression.range(),
                        None,
                        module_info,
                        transaction,
                        handle,
                        answers,
                    )
                    .into_iter()
                    .for_each(|callee| {
                        res.push((module_info.display_range(dec.expression.range()), callee));
                    });
                }
            }
        }

        for stmt in &ast.body {
            match &stmt {
                Stmt::ClassDef(StmtClassDef {
                    decorator_list: d, ..
                })
                | Stmt::FunctionDef(StmtFunctionDef {
                    decorator_list: d, ..
                }) => {
                    add_decorators(d, &module_info, &answers, &transaction, &handle, &mut res);
                }
                _ => {}
            }
            stmt.visit(&mut |x| {
                process_expr(x, &module_info, &answers, &transaction, &handle, &mut res)
            });
        }

        Some(res)
    }

    pub fn get_types_in_file(
        &self,
        name: ModuleName,
        path: ModulePath,
    ) -> Option<Vec<(DisplayRange, String)>> {
        let handle = self.make_handle(name, path);

        let transaction = self.state.transaction();
        let ast = transaction.get_ast(&handle)?;
        let module_info = transaction.get_module_info(&handle)?;
        let answers = transaction.get_answers(&handle)?;
        let bindings = transaction.get_bindings(&handle)?;

        let mut res = Vec::new();

        fn add_type(
            ty: &Type,
            e: &Expr,
            parent: Option<&Expr>,
            range: TextRange,
            module_info: &ModuleInfo,
            res: &mut Vec<(DisplayRange, String)>,
        ) {
            res.push((
                display_range_for_expr(module_info, range, e, parent),
                type_to_string(ty),
            ));
        }
        fn try_find_key_for_name(name: &ExprName, bindings: &Bindings) -> Option<Key> {
            let key = Key::BoundName(ShortIdentifier::expr_name(name));
            if bindings.is_valid_key(&key) {
                Some(key)
            } else if let key = Key::Definition(ShortIdentifier::expr_name(name))
                && bindings.is_valid_key(&key)
            {
                Some(key)
            } else {
                None
            }
        }
        fn f(
            x: &Expr,
            parent: Option<&Expr>,
            module_info: &ModuleInfo,
            answers: &Answers,
            bindings: &Bindings,
            res: &mut Vec<(DisplayRange, String)>,
        ) {
            let range = x.range();
            if let Expr::Name(name) = x
                && let Some(key) = try_find_key_for_name(name, bindings)
                && let Some(ty) = answers.get_type_at(bindings.key_to_idx(&key))
            {
                add_type(&ty, x, parent, range, module_info, res);
            } else if let Some(ty) = answers.get_type_trace(range) {
                add_type(&ty, x, parent, range, module_info, res);
            }
            x.recurse(&mut |c| f(c, Some(x), module_info, answers, bindings, res));
        }

        ast.visit(&mut |x| f(x, None, &module_info, &answers, &bindings, &mut res));
        Some(res)
    }

    /// Given an expression, which contains qualified types, guess which imports to add.
    ///
    /// For example `foo.bar.baz` will return `[foo.bar]`.
    ///
    /// The expression comes in as a module because we are parsing it from a raw string
    /// input; we expect it to actually be a type expression.
    fn find_imports(module: &ModModule, t: &Transaction, h: &Handle) -> Vec<String> {
        fn compute_prefix(attr: &ExprAttribute) -> Option<Vec<&Name>> {
            match &*attr.value {
                Expr::Attribute(base) => {
                    let mut res = compute_prefix(base)?;
                    res.push(&base.attr.id);
                    Some(res)
                }
                Expr::Name(base) => Some(vec![&base.id]),
                _ => None,
            }
        }

        fn collect_attribute_prefixes(
            x: &Expr,
            res: &mut SmallSet<String>,
            t: &Transaction,
            h: &Handle,
        ) {
            if let Expr::Attribute(attr) = x {
                // `attr` is a qname of a type. Get its prefix, which is likely the
                // module where it is defined.
                if let Some(mut names) = compute_prefix(attr) {
                    // The initial prefix may not be an actual module, if the type in question
                    // is a nested class. Search recursively for the longest part of the prefix
                    // that is a module, and assume that is where the type is defined.
                    //
                    // Note: in messy codebases that include name collisions between submodules
                    // and attributes of `__init__.py` modules, this rule can fail (in this
                    // scenario it's also possible for the qname to be ambiguous, as in two
                    // distinct types have the same qname). We do not support such codebases.
                    loop {
                        if !names.is_empty() {
                            let module_name = names.map(|name| name.as_str()).join(".");
                            if t.import_handle(
                                h,
                                ModuleName::from_string(module_name.clone()),
                                None,
                            )
                            .is_ok()
                            {
                                // We found the longest matching prefix, assume this is the import.
                                res.insert(names.map(|name| name.as_str()).join("."));
                                break;
                            } else {
                                // No module at this prefix, keep looking.
                                names.pop();
                            }
                        } else {
                            // If we get here, either the name is undefined or it is is defined in `builtins`;
                            // either way we can skip it.
                            break;
                        }
                    }
                }
            } else {
                x.recurse(&mut |x| collect_attribute_prefixes(x, res, t, h));
            }
        }
        let mut res = SmallSet::new();
        module.visit(&mut |x| collect_attribute_prefixes(x, &mut res, t, h));
        res.into_iter().collect()
    }

    /// Check a snippet of code; used as part of performing is_subtype checks via the query API.
    fn check_code_snippet(
        &self,
        name: ModuleName,
        path: PathBuf,
        lt: &str,
        gt: &str,
        types: String,
        check: &'static str,
    ) -> Result<bool, String> {
        let mut t = self.state.transaction();
        let h = self.make_handle(name, ModulePath::memory(path.clone()));
        let imported = Query::find_imports(&Ast::parse(&types).0, &t, &h);
        let imports = imported.map(|x| format!("import {x}\n")).join("");

        // First, make sure that the types are well-formed and importable, return `Err` if not
        let before = format!("{imports}\n{types}\n");
        t.set_memory(vec![(path.clone(), Some(Arc::new(before.clone())))]);
        t.run(&[h.dupe()], Require::Everything);
        let errors = t.get_errors([&h]).collect_errors();
        if !errors.shown.is_empty() {
            let mut res = Vec::new();
            let project_root = PathBuf::new();
            for e in errors.shown {
                e.write_line(&mut Cursor::new(&mut res), project_root.as_path(), true)
                    .unwrap();
            }
            return Err(format!(
                "Errors from is_subtype `{lt}` <: `{gt}`\n{}\n\nSource code:\n{before}",
                str::from_utf8(&res).unwrap_or("UTF8 error")
            ));
        }

        // Now that we know the types are valid, check a snippet to do the actual subtype test.
        let after = format!("{imports}\n{types}\n{check}");
        t.set_memory(vec![(path, Some(Arc::new(after)))]);
        t.run(&[h.dupe()], Require::Everything);
        let errors = t.get_errors([&h]).collect_errors();
        Ok(errors.shown.is_empty())
    }

    /// Return `Err` if you can't resolve them to types, otherwise return `lt <: gt`.
    pub fn is_subtype(
        &self,
        name: ModuleName,
        path: PathBuf,
        lt: &str,
        gt: &str,
    ) -> Result<bool, String> {
        println!("At is_subtype top level");
        if gt == "TypedDictionary" || gt == "NonTotalTypedDictionary" {
            // For backward compatibility with Pyre, we allow `is_subset` comparison for checking if something
            // is a TypedDict. That isn't actually a valid subtype relationship, so we look for magic
            // attributes that in practice only exist on typed dicts.
            let types = format!("pyrefly_lt = ({lt})");
            let check =
                "pyrefly_lt.__required_keys__, pyrefly_lt.__optional_keys__, pyrefly_lt.__total__";
            self.check_code_snippet(name, path, lt, gt, types, check)
        } else {
            // In the normal case, synthesize a function whose return is a type error if the subset fails.
            let types = format!("type pyrefly_lt = ({lt})\ntype pyrefly_gt = ({gt})\n");
            let check = "def pyrefly_func(x: pyrefly_lt) -> pyrefly_gt:\n    return x";
            self.check_code_snippet(name, path, lt, gt, types, check)
        }
    }
}
