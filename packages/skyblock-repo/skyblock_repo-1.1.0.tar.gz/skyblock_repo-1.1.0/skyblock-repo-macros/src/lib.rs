use heck::ToPascalCase;
use proc_macro::TokenStream;
use quote::quote;
use syn::{DeriveInput, Ident, parse_macro_input};

#[proc_macro]
pub fn getter(input: TokenStream) -> TokenStream {
	let ident = parse_macro_input!(input as Ident);
	let base = ident.to_string();

	let pascal = base.to_pascal_case();
	let plural = format!("{base}s");
	let method = format!("get_{base}_by_id");

	let pascal_ident = syn::Ident::new(&format!("Skyblock{pascal}"), ident.span());
	let plural_ident = syn::Ident::new(&plural, ident.span());
	let method_ident = syn::Ident::new(&method, ident.span());

	let expanded = quote! {
		#[doc = concat!("Retrieves a `", stringify!($name), "` by its `internalId`.")]
		#[must_use]
		#[inline]
		pub fn #method_ident(&self, id: &str) -> Option<#pascal_ident> {
			self.#plural_ident.get(&id.to_uppercase()).cloned()
		}
	};

	expanded.into()
}

#[proc_macro_derive(PyStr)]
pub fn derive_pystr(input: TokenStream) -> TokenStream {
	let input = parse_macro_input!(input as DeriveInput);
	let name = &input.ident;

	let expanded = quote! {
		#[pymethods]
		impl #name {
			fn __str__(&self) -> String {
				serde_json::to_string(self).unwrap()
			}
		}
	};

	expanded.into()
}
