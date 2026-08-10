"use client";

import React from "react";

function isSafeUrl(url) {
  const trimmed = (url || "").trim();
  if (/^(\/|\.\/|\.\.\/|#)/.test(trimmed)) return true;
  try {
    const parsed = new URL(trimmed, "https://example.com");
    return ["http:", "https:", "mailto:", "tel:"].includes(parsed.protocol);
  } catch {
    return false;
  }
}

function renderInlineText(text) {
  if (!text) return null;

  const inlineRegex =
    /\*\*(?<bold>[^*]+)\*\*|~~(?<strike>[^~]+)~~|\*(?<italicStar>[^*]+)\*|(?<!\w)_(?<italicUnder>[^_\s][^_]*?)_(?!\w)|`(?<inlineCode>[^`]+)`|\[(?<linkText>[^\]]+)\]\((?<linkUrl>[^)\s]+)\)/;

  const tokens = [];
  let remaining = text;
  let keyIdx = 0;

  while (remaining) {
    const match = remaining.match(inlineRegex);
    if (!match || match.index === undefined) {
      tokens.push(remaining);
      break;
    }

    const matchIndex = match.index;
    if (matchIndex > 0) {
      tokens.push(remaining.substring(0, matchIndex));
    }

    const groups = match.groups || {};

    if (groups.bold !== undefined) {
      tokens.push(
        <strong
          key={`b-${keyIdx++}`}
          className="font-extrabold text-slate-900 dark:text-white"
        >
          {groups.bold}
        </strong>,
      );
    } else if (groups.strike !== undefined) {
      tokens.push(
        <del
          key={`s-${keyIdx++}`}
          className="line-through text-slate-500 dark:text-slate-400"
        >
          {groups.strike}
        </del>,
      );
    } else if (
      groups.italicStar !== undefined ||
      groups.italicUnder !== undefined
    ) {
      tokens.push(
        <em
          key={`i-${keyIdx++}`}
          className="italic text-slate-700 dark:text-slate-300"
        >
          {groups.italicStar ?? groups.italicUnder}
        </em>,
      );
    } else if (groups.inlineCode !== undefined) {
      tokens.push(
        <code
          key={`c-${keyIdx++}`}
          className="bg-slate-100 dark:bg-slate-800 text-[#285872] dark:text-[#58a0c9] px-1.5 py-0.5 rounded text-[11px] font-mono border border-slate-200 dark:border-slate-750"
        >
          {groups.inlineCode}
        </code>,
      );
    } else if (groups.linkText !== undefined) {
      const safe = isSafeUrl(groups.linkUrl);
      tokens.push(
        safe ? (
          <a
            key={`a-${keyIdx++}`}
            href={groups.linkUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#285872] dark:text-[#58a0c9] underline hover:opacity-80 font-bold"
          >
            {groups.linkText}
          </a>
        ) : (
          <span key={`a-${keyIdx++}`}>{groups.linkText}</span>
        ),
      );
    }

    remaining = remaining.substring(matchIndex + match[0].length);
  }

  return tokens;
}

function parseTableRow(line) {
  const trimmed = line.trim();
  const content = trimmed.replace(/^\|/, "").replace(/\|$/, "");
  return content
    .split(/(?<!\\)\|/)
    .map((cell) => cell.trim().replace(/\\\|/g, "|"));
}

function isTableDelimiterRow(line) {
  const trimmed = line.trim();
  if (!trimmed.includes("|") || !trimmed.includes("-")) return false;
  const cells = parseTableRow(trimmed);
  return (
    cells.length > 0 &&
    cells.every((cell) => /^:?-+:?$/.test(cell.replace(/\s+/g, "")))
  );
}

function getColumnAlignments(delimiterLine) {
  const cells = parseTableRow(delimiterLine);
  return cells.map((cell) => {
    const clean = cell.replace(/\s+/g, "");
    if (clean.startsWith(":") && clean.endsWith(":")) return "text-center";
    if (clean.endsWith(":")) return "text-right";
    return "text-left";
  });
}

function isHorizontalRule(line) {
  const compact = line.replace(/\s+/g, "");
  return /^(-{3,}|\*{3,}|_{3,})$/.test(compact);
}

function parseListMarker(line) {
  const match = line.match(/^(\s*)(?:([*\-•])|(\d+)\.)\s+(.*)$/);
  if (!match) return null;
  return {
    indent: match[1].length,
    ordered: match[3] !== undefined,
    start: match[3] !== undefined ? parseInt(match[3], 10) : null,
    content: match[4],
  };
}

function buildList(lines, index, baseIndent) {
  const first = parseListMarker(lines[index]);
  const ordered = first.ordered;
  const items = [];
  let i = index;

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) {
      let j = i + 1;
      while (j < lines.length && !lines[j].trim()) j++;
      if (j >= lines.length) {
        i = j;
        break;
      }
      const peek = parseListMarker(lines[j]);
      if (!peek || peek.indent < baseIndent) {
        i = j;
        break;
      }
      i = j;
      continue;
    }

    const marker = parseListMarker(line);
    if (!marker || marker.indent < baseIndent) break;

    if (marker.indent > baseIndent) {
      const [nestedNode, nextIndex] = buildList(lines, i, marker.indent);
      if (items.length) items[items.length - 1].children.push(nestedNode);
      i = nextIndex;
      continue;
    }

    if (marker.ordered !== ordered) break;

    items.push({ content: marker.content, children: [] });
    i++;
  }

  return [{ ordered, start: first.start ?? 1, items }, i];
}

function renderListTree(tree, key) {
  const Tag = tree.ordered ? "ol" : "ul";
  const sharedClass =
    "space-y-1.5 my-2 text-xs font-medium text-slate-750 dark:text-slate-300 leading-relaxed";
  const tagProps = tree.ordered
    ? {
        className: `list-decimal pl-5 ${sharedClass}`,
        start: tree.start !== 1 ? tree.start : undefined,
      }
    : { className: sharedClass };

  return (
    <Tag key={key} {...tagProps}>
      {tree.items.map((item, idx) => {
        const checkboxMatch = item.content.match(/^\[( |x|X)\]\s+(.*)$/);
        return (
          <li
            key={idx}
            className={tree.ordered ? "pl-1" : "flex items-start gap-2"}
          >
            {!tree.ordered &&
              (checkboxMatch ? (
                <input
                  type="checkbox"
                  checked={checkboxMatch[1].toLowerCase() === "x"}
                  readOnly
                  className="mt-1 accent-[#285872] dark:accent-[#58a0c9] shrink-0"
                />
              ) : (
                <span className="w-1.5 h-1.5 bg-[#285872] dark:bg-[#58a0c9] rounded-full shrink-0 mt-1.5" />
              ))}
            <div className={tree.ordered ? "" : "flex-1"}>
              {renderInlineText(
                checkboxMatch ? checkboxMatch[2] : item.content,
              )}
              {item.children.map((child, cIdx) =>
                renderListTree(child, `n-${idx}-${cIdx}`),
              )}
            </div>
          </li>
        );
      })}
    </Tag>
  );
}

function isBlockLine(line, lines, idx) {
  const t = line.trim();
  if (!t) return true;
  if (t.startsWith("```")) return true;
  if (isHorizontalRule(t)) return true;
  if (/^#{1,4}\s+/.test(t)) return true;
  if (parseListMarker(line)) return true;
  if (t.startsWith(">")) return true;
  if (
    t.includes("|") &&
    idx + 1 < lines.length &&
    isTableDelimiterRow(lines[idx + 1])
  )
    return true;
  return false;
}

function MarkdownRendererComponent({ content, className = "" }) {
  if (!content) return null;
  const source = typeof content === "string" ? content : String(content);

  const lines = source.split("\n");
  const elements = [];
  let elementKey = 0;

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (!trimmed) continue;

    if (trimmed.startsWith("```")) {
      const lang = trimmed.slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      elements.push(
        <div
          key={`code-${elementKey++}`}
          className="my-3 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden"
        >
          {lang && (
            <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
              {lang}
            </div>
          )}
          <pre className="overflow-x-auto p-3 bg-slate-50 dark:bg-slate-900">
            <code className="text-[11px] font-mono text-slate-800 dark:text-slate-200 whitespace-pre">
              {codeLines.join("\n")}
            </code>
          </pre>
        </div>,
      );
      continue;
    }

    if (
      trimmed.includes("|") &&
      i + 1 < lines.length &&
      isTableDelimiterRow(lines[i + 1])
    ) {
      const headers = parseTableRow(trimmed);
      const alignments = getColumnAlignments(lines[i + 1]);
      const tableRows = [];
      i += 2;

      while (i < lines.length && lines[i].trim() && lines[i].includes("|")) {
        tableRows.push(parseTableRow(lines[i]));
        i++;
      }
      i--;

      elements.push(
        <div
          key={`table-${elementKey++}`}
          className="my-3 overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm"
        >
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-100 dark:bg-slate-800/80 text-slate-900 dark:text-slate-100 font-bold border-b border-slate-200 dark:border-slate-700">
              <tr>
                {headers.map((header, hIdx) => (
                  <th
                    key={`th-${hIdx}`}
                    className={`px-3 py-2.5 font-bold ${alignments[hIdx] || "text-left"}`}
                  >
                    {renderInlineText(header)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-750 dark:text-slate-300">
              {tableRows.map((row, rIdx) => (
                <tr
                  key={`tr-${rIdx}`}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
                >
                  {row.map((cell, cIdx) => (
                    <td
                      key={`td-${cIdx}`}
                      className={`px-3 py-2 leading-relaxed ${alignments[cIdx] || "text-left"}`}
                    >
                      {renderInlineText(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }

    if (isHorizontalRule(trimmed)) {
      elements.push(
        <hr
          key={`hr-${elementKey++}`}
          className="my-4 border-slate-200 dark:border-slate-800"
        />,
      );
      continue;
    }

    if (trimmed.startsWith("#### ")) {
      elements.push(
        <h4
          key={`h4-${elementKey++}`}
          className="text-xs font-black uppercase tracking-wider text-[#285872] dark:text-[#58a0c9] mt-3 mb-1"
        >
          {renderInlineText(
            trimmed.replace(/^####\s+/, "").replace(/\s+#+$/, ""),
          )}
        </h4>,
      );
      continue;
    }

    if (trimmed.startsWith("### ")) {
      elements.push(
        <h3
          key={`h3-${elementKey++}`}
          className="text-sm font-extrabold text-slate-900 dark:text-white mt-3 mb-1"
        >
          {renderInlineText(
            trimmed.replace(/^###\s+/, "").replace(/\s+#+$/, ""),
          )}
        </h3>,
      );
      continue;
    }

    if (trimmed.startsWith("## ")) {
      elements.push(
        <h2
          key={`h2-${elementKey++}`}
          className="text-base font-extrabold text-slate-900 dark:text-white mt-4 mb-1 border-b border-slate-100 dark:border-slate-800 pb-1"
        >
          {renderInlineText(
            trimmed.replace(/^##\s+/, "").replace(/\s+#+$/, ""),
          )}
        </h2>,
      );
      continue;
    }

    if (trimmed.startsWith("# ")) {
      elements.push(
        <h1
          key={`h1-${elementKey++}`}
          className="text-lg font-black text-slate-900 dark:text-white mt-4 mb-2"
        >
          {renderInlineText(trimmed.replace(/^#\s+/, "").replace(/\s+#+$/, ""))}
        </h1>,
      );
      continue;
    }

    const listMarker = parseListMarker(rawLine);
    if (listMarker) {
      const [tree, nextIndex] = buildList(lines, i, listMarker.indent);
      elements.push(renderListTree(tree, `list-${elementKey++}`));
      i = nextIndex - 1;
      continue;
    }

    if (trimmed.startsWith(">")) {
      const quoteLines = [trimmed.replace(/^>\s?/, "")];
      let j = i + 1;
      while (j < lines.length && lines[j].trim().startsWith(">")) {
        quoteLines.push(lines[j].trim().replace(/^>\s?/, ""));
        j++;
      }
      i = j - 1;
      elements.push(
        <blockquote
          key={`quote-${elementKey++}`}
          className="border-l-4 border-[#285872] pl-3 py-1 my-2 bg-slate-50 dark:bg-slate-950/60 rounded-r-xl text-xs italic text-slate-650 dark:text-slate-350"
        >
          {quoteLines.map((line, idx) => (
            <React.Fragment key={idx}>
              {idx > 0 && <br />}
              {renderInlineText(line)}
            </React.Fragment>
          ))}
        </blockquote>,
      );
      continue;
    }

    const paragraphLines = [trimmed];
    let j = i + 1;
    while (j < lines.length && !isBlockLine(lines[j], lines, j)) {
      paragraphLines.push(lines[j].trim());
      j++;
    }
    i = j - 1;
    elements.push(
      <p
        key={`p-${elementKey++}`}
        className="text-xs font-medium text-slate-800 dark:text-slate-200 leading-relaxed my-1"
      >
        {paragraphLines.map((line, idx) => (
          <React.Fragment key={idx}>
            {idx > 0 && <br />}
            {renderInlineText(line)}
          </React.Fragment>
        ))}
      </p>,
    );
  }

  return <div className={`space-y-1 ${className}`}>{elements}</div>;
}

export default React.memo(MarkdownRendererComponent);
