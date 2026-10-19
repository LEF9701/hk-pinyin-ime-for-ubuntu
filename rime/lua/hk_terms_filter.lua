-- 港式拼音: Hong Kong vocabulary filter.
--
-- For every candidate whose text contains a mainland / Taiwan term
-- (軟體, 網路, 計程車, 冰箱 …), put the Hong Kong form first and keep the
-- original right after it, so  bingxiang → 雪櫃 | 冰箱 | …
--
-- The term list lives in opencc/hk_terms.txt; the switch is "hk_terms".

local M = {}

function M.init(env)
  local ok, cc = pcall(Opencc, "hk_terms.json")
  env.cc = ok and cc or nil
  if not env.cc then
    log.warning("hk_terms_filter: cannot load opencc/hk_terms.json")
  end
end

function M.func(input, env)
  local on = env.engine.context:get_option("hk_terms")
  for cand in input:iter() do
    if on and env.cc then
      local hk = env.cc:convert(cand.text)
      if hk and hk ~= "" and hk ~= cand.text then
        yield(ShadowCandidate(cand, cand.type, hk, cand.comment))
      end
    end
    yield(cand)
  end
end

function M.fini(env)
  env.cc = nil
end

return M
