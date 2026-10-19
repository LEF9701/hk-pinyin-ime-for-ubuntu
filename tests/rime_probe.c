/*
 * rime_probe — type pinyin into the hk_pinyin schema without a desktop
 * and print the candidate list. Used by tests/run_tests.sh.
 *
 *   rime_probe <user_data_dir> <shared_data_dir> <input> [<input> ...]
 *
 * An input such as "ruanjian" is typed key by key; the first page of
 * candidates is printed as:  ruanjian ⇒ 軟件 | 軟件 | …
 * Prefix an input with '!' to toggle an option first, e.g. "!hk_terms".
 */
#include <rime_api.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
  if (argc < 4) {
    fprintf(stderr, "usage: %s user_dir shared_dir input...\n", argv[0]);
    return 2;
  }
  RimeApi *rime = rime_get_api();
  RIME_STRUCT(RimeTraits, traits);
  traits.app_name = "rime.hk_pinyin_probe";
  traits.user_data_dir = argv[1];
  traits.shared_data_dir = argv[2];
  traits.distribution_name = "hk-pinyin-probe";
  traits.distribution_code_name = "probe";
  traits.distribution_version = "1";
  traits.min_log_level = 2;
  rime->setup(&traits);
  rime->initialize(&traits);
  if (rime->start_maintenance(True)) rime->join_maintenance_thread();

  RimeSessionId s = rime->create_session();
  if (!rime->select_schema(s, "hk_pinyin")) {
    fprintf(stderr, "cannot select schema hk_pinyin\n");
    return 1;
  }
  int rc = 0;
  for (int i = 3; i < argc; ++i) {
    const char *in = argv[i];
    if (in[0] == '!') {
      Bool v = rime->get_option(s, in + 1);
      rime->set_option(s, in + 1, !v);
      printf("[option %s = %d]\n", in + 1, !v);
      continue;
    }
    rime->clear_composition(s);
    for (const char *p = in; *p; ++p) rime->process_key(s, (unsigned char)*p, 0);

    RIME_STRUCT(RimeCommit, commit);
    if (rime->get_commit(s, &commit)) {
      printf("%s ⇒ [commit] %s\n", in, commit.text);
      rime->free_commit(&commit);
      continue;
    }
    RIME_STRUCT(RimeContext, ctx);
    if (!rime->get_context(s, &ctx)) { rc = 1; continue; }
    printf("%s ⇒", in);
    for (int j = 0; j < ctx.menu.num_candidates; ++j) {
      printf(" %s%s", j ? "| " : "", ctx.menu.candidates[j].text);
      if (ctx.menu.candidates[j].comment && *ctx.menu.candidates[j].comment)
        printf("〔%s〕", ctx.menu.candidates[j].comment);
    }
    printf("\n");
    rime->free_context(&ctx);
  }
  rime->destroy_session(s);
  rime->finalize();
  return rc;
}
