import { useMemo } from "react";

interface Props {
  title: string;
  markdown: string;
}

/**
 * Hyvin kevyt markdown-renderi — ei haluta tuoda raskasta kirjastoa riippuvuutena
 * pelkästään otsikoiden ja lainausten esittämiseen. Karpathy-kurin mukaan:
 * mahdollisimman vähän riippuvuuksia, tuloksena teknisesti tyylikäs näkymä.
 */
function renderMarkdown(md: string): React.ReactNode {
  const lines = md.split(/\r?\n/);
  const nodes: React.ReactNode[] = [];
  let inCode = false;
  let codeBuf: string[] = [];

  const flushCode = (key: number) => {
    nodes.push(
      <pre
        key={`code-${key}`}
        className="my-3 overflow-x-auto rounded border border-panel_oxidized/60 bg-base_bg/80 p-3 font-code text-[12px] text-accent_amber"
      >
        {codeBuf.join("\n")}
      </pre>,
    );
    codeBuf = [];
  };

  lines.forEach((raw, idx) => {
    if (raw.startsWith("```")) {
      if (inCode) {
        flushCode(idx);
        inCode = false;
      } else {
        inCode = true;
      }
      return;
    }
    if (inCode) {
      codeBuf.push(raw);
      return;
    }
    if (raw.startsWith("# ")) {
      nodes.push(
        <h1 key={idx} className="mt-4 font-heading text-xl font-semibold tracking-wide text-ink_soft">
          {raw.slice(2)}
        </h1>,
      );
    } else if (raw.startsWith("## ")) {
      nodes.push(
        <h2 key={idx} className="mt-4 font-heading text-base font-semibold tracking-wide text-accent_amber/90">
          {raw.slice(3)}
        </h2>,
      );
    } else if (raw.startsWith("### ")) {
      nodes.push(
        <h3 key={idx} className="mt-3 font-heading text-sm font-semibold tracking-wide text-ink_soft/90">
          {raw.slice(4)}
        </h3>,
      );
    } else if (raw.startsWith("> ")) {
      nodes.push(
        <blockquote
          key={idx}
          className="my-2 border-l-2 border-copper_reveal/70 bg-panel_oxidized/20 px-3 py-1 font-heading text-sm italic text-ink_soft/90"
        >
          {raw.slice(2)}
        </blockquote>,
      );
    } else if (raw.trim().startsWith("- ")) {
      nodes.push(
        <li key={idx} className="ml-5 list-disc text-sm text-ink_soft/85">
          {raw.trim().slice(2)}
        </li>,
      );
    } else if (raw.trim().length === 0) {
      nodes.push(<div key={idx} className="h-2" />);
    } else {
      nodes.push(
        <p key={idx} className="text-sm leading-relaxed text-ink_soft/85">
          {raw}
        </p>,
      );
    }
  });
  if (inCode) flushCode(lines.length);
  return nodes;
}

export function PreviewPane({ title, markdown }: Props) {
  const rendered = useMemo(() => renderMarkdown(markdown), [markdown]);
  return (
    <div className="flex min-h-0 flex-col panel-inset">
      <div className="flex items-center justify-between border-b border-panel_oxidized/60 bg-base_bg/60 px-4 py-2">
        <span className="font-code text-[10px] uppercase tracking-[0.22em] text-ink_muted">
          {title}
        </span>
        <span className="font-code text-[10px] uppercase tracking-wider text-accent_amber/80">
          markdown
        </span>
      </div>
      <div className="flex-1 overflow-y-auto px-5 py-4">{rendered}</div>
    </div>
  );
}
