#include "elib.h"
#include "ecru.h"
#include "vm.h"
#if OLD_GIO
#include <gio/gfile.h>
#include <gio/gfileinputstream.h>
#endif

static e_Ref e_module_fileopen(GString *modName) {
  GError *err = NULL;
  GString *fullModName = g_string_sized_new(modName->len + 3);
  g_string_assign(fullModName, modName->str);
  g_string_append(fullModName, ".ec");
  GFile *parent = g_file_new_for_path(ECRU_BYTECODE_DIR);
  GFile *modFile = g_file_get_child(parent, fullModName->str);
  GFileInputStream *stream = g_file_read(modFile, NULL, &err);
  if (stream == NULL || err != NULL) {
    return e_throw_pair("Not found", e_make_gstring(modName));
  }
  return e_make_reader((GInputStream *)stream);
}

e_Ref e_module_import(GString *modName) {
  e_Ref modfile = e_module_fileopen(modName);
  E_ERROR_CHECK(modfile);
  ecru_module *mod = ecru_load_bytecode(modfile, e_safeScope);
  if (mod == NULL) {
    /* propagate the exception */
    return e_empty_ref;
  }
  return ecru_vm_execute(0, 0, false, NULL, mod, NULL, 0, NULL);
}
