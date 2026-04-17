import Editor from "@monaco-editor/react";

interface Props {
  title: string;
  language: "yaml" | "markdown";
  value: string;
  onChange: (value: string) => void;
}

export function EditorPane({ title, language, value, onChange }: Props) {
  return (
    <div className="flex min-h-0 flex-col panel-inset">
      <div className="flex items-center justify-between border-b border-panel_oxidized/60 bg-base_bg/60 px-4 py-2">
        <span className="font-code text-[10px] uppercase tracking-[0.22em] text-ink_muted">
          {title}
        </span>
        <span className="font-code text-[10px] uppercase tracking-wider text-accent_amber/80">
          {language}
        </span>
      </div>
      <div className="monaco-shell flex-1">
        <Editor
          height="100%"
          defaultLanguage={language}
          language={language}
          value={value}
          onChange={(v) => onChange(v ?? "")}
          theme="vs-dark"
          options={{
            fontFamily: '"JetBrains Mono", ui-monospace, monospace',
            fontSize: 13,
            lineNumbers: "on",
            minimap: { enabled: false },
            renderLineHighlight: "gutter",
            smoothScrolling: true,
            scrollBeyondLastLine: false,
            padding: { top: 12 },
            wordWrap: "on",
            tabSize: 2,
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  );
}
