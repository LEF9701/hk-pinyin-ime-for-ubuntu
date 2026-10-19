-- 港式拼音: dates and times in Hong Kong formats.
--
--   rq  日期   2026年10月19日 · 19/10/2026 · 二〇二六年十月十九日 · 2026-10-19
--   sj  時間   下午3:05 · 15:05 · 下午三時零五分
--   xq  星期   星期一 · 週一 · （一）
--   dt  日期時間 2026年10月19日（星期一）下午3:05

local DIGITS = { [0] = "〇", "一", "二", "三", "四", "五", "六", "七", "八", "九" }
local WEEKDAYS = { [0] = "日", "一", "二", "三", "四", "五", "六" }

-- 0–99 as Chinese numerals: 5 → 五, 10 → 十, 21 → 二十一
local function cn_number(n)
  if n < 10 then return DIGITS[n] end
  local tens, ones = math.floor(n / 10), n % 10
  local s = (tens == 1) and "十" or (DIGITS[tens] .. "十")
  if ones > 0 then s = s .. DIGITS[ones] end
  return s
end

local function cn_year(y)
  return (tostring(y):gsub("%d", function(d) return DIGITS[tonumber(d)] end))
end

-- Hong Kong style period of day for a 12-hour clock
local function period(h)
  if h < 6 then return "凌晨"
  elseif h < 12 then return "上午"
  elseif h < 18 then return "下午"
  else return "晚上" end
end

local function hour12(h)
  local x = h % 12
  if x == 0 then x = 12 end
  return x
end

local function cn_time(h, m)
  local s = period(h) .. cn_number(hour12(h)) .. "時"
  if m == 0 then return s .. "正" end
  if m < 10 then return s .. "零" .. DIGITS[m] .. "分" end
  return s .. cn_number(m) .. "分"
end

local function make(input, seg, items, tag)
  for _, item in ipairs(items) do
    local c = Candidate(tag, seg.start, seg._end, item[1], item[2] or "")
    c.quality = 1000
    yield(c)
  end
end

local function translator(input, seg, env)
  local t = os.date("*t")
  local y, mo, d, h, mi = t.year, t.month, t.day, t.hour, t.min
  local wd = WEEKDAYS[t.wday - 1]

  if input == "rq" then
    make(input, seg, {
      { string.format("%d年%d月%d日", y, mo, d) },
      { string.format("%02d/%02d/%d", d, mo, y), "日/月/年" },
      { cn_year(y) .. "年" .. cn_number(mo) .. "月" .. cn_number(d) .. "日" },
      { string.format("%d-%02d-%02d", y, mo, d), "ISO" },
    }, "date")
  elseif input == "sj" then
    make(input, seg, {
      { string.format("%s%d:%02d", period(h), hour12(h), mi) },
      { string.format("%02d:%02d", h, mi) },
      { cn_time(h, mi) },
    }, "time")
  elseif input == "xq" then
    make(input, seg, {
      { "星期" .. wd },
      { "週" .. wd },
      { "（" .. wd .. "）" },
    }, "weekday")
  elseif input == "dt" then
    make(input, seg, {
      { string.format("%d年%d月%d日（星期%s）%s%d:%02d", y, mo, d, wd, period(h), hour12(h), mi) },
      { string.format("%02d/%02d/%d %02d:%02d", d, mo, y, h, mi) },
    }, "datetime")
  end
end

return translator
