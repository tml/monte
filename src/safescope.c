#include <string.h>
#include "elib.h"


#if OLD_GIO
#include <gio/gmemoryoutputstream.h>
#include <gio/gseekable.h>
#endif


e_Ref e_safeScope;


void e__safescope_set_up() {
  e_make_script(&e__equalizer_script, NULL, equalizer_methods, "Equalizer");
  e_make_script(&e__comparer_script, NULL, comparer_methods, "Comparer");
  e_make_script(&e__looper_script, NULL, looper_methods, "Loop");
  e_make_script(&e__makeList_script, makeList_dispatch, makeList_methods,
                "ConstList__Maker");
  e_make_script(&e__makeMap_script, NULL, makeMap_methods,
                "ConstMap__Maker");
  e_make_script(&e__orderedSpace_script, NULL, orderedSpace_methods,
                "OrderedRegion");
  e_make_script(&e__descender_script, NULL, descender_methods,
                "descender");
  e_make_script(&e__makeOrderedSpace_script, NULL, makeOrderedSpace_methods,
                "makeOrderedRegion");
  e_make_script(&e__require_script, NULL, require_methods,
                "require");
  e_make_script(&e__test_script, NULL, test_methods,
                "__Test");
  e_make_script(&viafunc1_script, NULL, viafunc1_methods, "viaFunc1");
  e_make_script(&viafunc2_script, NULL, viafunc2_methods, "viaFunc2");
  e_make_script(&e__bind_script, NULL, bind_methods, "__bind");
  e_make_script(&isSameFunc_script, NULL, isSameFunc_methods, "__isSameFunc");
  e_make_script(&e__is_script, NULL, is_methods, "__is");
  e_make_script(&verbFacet_script, verbFacet_dispatch, no_methods,
                "verbFacet");
  e_make_script(&e__makeVerbFacet_script, NULL, makeVerbFacet_methods,
                "__makeVerbFacet");
  e_make_script(&e__suchThat_script, NULL, suchThat_methods,
                "__suchThat");
  e_make_script(&suchThatFuncFalse_script, NULL, suchThatFuncFalse_methods,
                "suchThatFunc");
  e_make_script(&suchThatFuncTrue_script, NULL, suchThatFuncTrue_methods,
                "suchThatFunc");
  e_make_script(&thrower_script, NULL, thrower_methods,
                "thrower");
  e_make_script(&simple__quasiParser_script, NULL, simple__quasiParser_methods,
                "simple__quasiParser");
  e_make_script(&substituter_script, NULL, substituter_methods,
                "textSubstituter");
  e_make_script(&import__uriGetter_script, NULL, import__uriGetter_methods,
                "import__uriGetter");
  e_make_script(&THE_E_script, NULL, THE_E_methods, "E");
  e_make_script(&e__traceln_script, NULL, e__traceln_methods, "traceln");
  e_thrower.script = &thrower_script;
  e_equalizer.script = &e__equalizer_script;
  e_comparer.script = &e__comparer_script;
  e_looper.script = &e__looper_script;
  e_makeList.script = &e__makeList_script;
  e_makeMap.script = &e__makeMap_script;
  e_require.script = &e__require_script;
  e_makeOrderedSpace.script = &e__makeOrderedSpace_script;
  e__Test.script = &e__test_script;
  e__bind.script = &e__bind_script;
  e__is.script = &e__is_script;
  e__makeVerbFacet.script = &e__makeVerbFacet_script;
  e__suchThat.script = &e__suchThat_script;
  e_simple__quasiParser.script = &simple__quasiParser_script;
  e_import__uriGetter.script = &import__uriGetter_script;
  e_traceln.script = &e__traceln_script;
  THE_E.script = &THE_E_script;
  e_make_selector(&op__cmp, "op__cmp", 1);
  e_make_selector(&belowZero, "belowZero", 0);
  e_make_selector(&atMostZero, "atMostZero", 0);
  e_make_selector(&isZero, "isZero", 0);
  e_make_selector(&atLeastZero, "atLeastZero", 0);
  e_make_selector(&aboveZero, "aboveZero", 0);
}