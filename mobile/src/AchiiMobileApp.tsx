import { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { AchiiStatusIndicator, type AchiiStatus } from "./components/AchiiStatusIndicator";
import { runLocalHarness } from "./lib/localInference";
import { mechanicalClick, mechanicalDing, mechanicalError } from "./lib/haptics";
import { tokens } from "./theme";

export function AchiiMobileApp() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState<AchiiStatus>("IDLE");
  const [latency, setLatency] = useState<number | null>(null);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const canRun = input.trim().length > 0 && status !== "PROCESSING";

  const onRun = useCallback(async () => {
    if (!canRun) return;
    setStatus("PROCESSING");
    setOutput("");
    setErrMsg(null);
    mechanicalClick();

    try {
      const result = await runLocalHarness(input);
      setOutput(result.summary);
      setLatency(result.ms);
      setStatus("SUCCESS");
      mechanicalDing();
    } catch (err) {
      setErrMsg(err instanceof Error ? err.message : String(err));
      setStatus("ERROR");
      mechanicalError();
    }
  }, [canRun, input]);

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.scrollContent}
      keyboardShouldPersistTaps="handled"
    >
      {/* HEADER */}
      <View style={styles.header}>
        <View style={styles.brandRow}>
          <View style={styles.brandDot} />
          <Text style={styles.brandTitle}>AGENTDIR</Text>
          <Text style={styles.brandSubtitle}>mobile</Text>
        </View>
        <View style={styles.headerPulse}>
          <Text style={styles.headerHint}>Edge AI · NPU</Text>
        </View>
      </View>

      {/* INPUT */}
      <View style={styles.inputBlock}>
        <Text style={styles.fieldLabel}>LIITÄ KONTEKSTI (.md data)</Text>
        <TextInput
          style={styles.textArea}
          value={input}
          onChangeText={setInput}
          multiline
          placeholder="Liitä tähän pitkä teksti prosessoitavaksi…"
          placeholderTextColor="#556070"
          selectionColor={tokens.colors.accent_amber}
          textAlignVertical="top"
          editable={status !== "PROCESSING"}
        />
      </View>

      {/* ACHII STATUS */}
      <View style={styles.statusBlock}>
        <AchiiStatusIndicator status={status} />
      </View>

      {/* RUN BUTTON */}
      <Pressable
        onPress={onRun}
        disabled={!canRun}
        style={({ pressed }) => [
          styles.runButton,
          !canRun && styles.runButtonDisabled,
          pressed && canRun && styles.runButtonPressed,
        ]}
      >
        {status === "PROCESSING" ? (
          <View style={styles.runButtonRow}>
            <ActivityIndicator color={tokens.colors.ink_soft} />
            <Text style={styles.runButtonText}>Prosessoi lokaalisti…</Text>
          </View>
        ) : (
          <Text style={styles.runButtonText}>Aja Lokaali Valjas</Text>
        )}
      </Pressable>

      {/* OUTPUT */}
      {output.length > 0 && (
        <View style={styles.outputBlock}>
          <Text style={styles.outputLabel}>ACHIIN TULOS (.yaml struktuuri)</Text>
          <Text style={styles.outputText}>{output}</Text>
          {latency !== null && (
            <Text style={styles.outputMeta}>
              Latenssi: {latency} ms · Gemma 2B · MediaPipe Edge AI
            </Text>
          )}
        </View>
      )}

      {/* ERROR */}
      {errMsg && (
        <View style={styles.errorBlock}>
          <Text style={styles.errorLabel}>VIRHE</Text>
          <Text style={styles.errorText}>{errMsg}</Text>
        </View>
      )}

      {/* FOOTER */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>Gemma 2B // MediaPipe Edge AI</Text>
        <View
          style={[
            styles.footerDot,
            status === "PROCESSING" && { backgroundColor: tokens.colors.accent_amber },
            status === "ERROR" && { backgroundColor: tokens.colors.error },
            status === "SUCCESS" && { backgroundColor: tokens.colors.success },
          ]}
        />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: {
    flex: 1,
    backgroundColor: tokens.colors.base_bg,
  },
  scrollContent: {
    paddingHorizontal: tokens.spacing.md,
    paddingTop: tokens.spacing.md,
    paddingBottom: tokens.spacing.xl,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingBottom: tokens.spacing.md,
    borderBottomColor: "rgba(44,62,80,0.5)",
    borderBottomWidth: 1,
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  brandDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: tokens.colors.accent_amber,
    shadowColor: tokens.colors.accent_amber,
    shadowOpacity: 0.8,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 0 },
  },
  brandTitle: {
    fontSize: 16,
    fontWeight: "700",
    letterSpacing: 3,
    color: tokens.colors.accent_amber,
  },
  brandSubtitle: {
    fontSize: 10,
    letterSpacing: 2,
    color: tokens.colors.ink_muted,
    textTransform: "uppercase",
  },
  headerPulse: {
    borderColor: "rgba(44,62,80,0.7)",
    borderWidth: 1,
    borderRadius: tokens.radius.sm,
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: "rgba(44,62,80,0.2)",
  },
  headerHint: {
    fontSize: 10,
    letterSpacing: 1.5,
    color: "#7DA6C6",
    textTransform: "uppercase",
  },
  inputBlock: {
    marginTop: tokens.spacing.lg,
    gap: tokens.spacing.sm,
  },
  fieldLabel: {
    fontSize: 11,
    letterSpacing: 2,
    color: tokens.colors.ink_muted,
  },
  textArea: {
    minHeight: 128,
    borderRadius: tokens.radius.md,
    borderWidth: 1,
    borderColor: tokens.colors.panel_oxidized,
    backgroundColor: tokens.colors.panel_fill,
    color: tokens.colors.ink_soft,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 14,
  },
  statusBlock: {
    marginTop: tokens.spacing.lg,
    alignItems: "center",
  },
  runButton: {
    marginTop: tokens.spacing.lg,
    borderRadius: tokens.radius.md,
    backgroundColor: tokens.colors.copper_reveal,
    paddingVertical: 16,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: tokens.colors.copper_reveal,
    shadowOpacity: 0.55,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 0 },
    elevation: 6,
  },
  runButtonPressed: {
    backgroundColor: tokens.colors.accent_amber,
  },
  runButtonDisabled: {
    backgroundColor: "#3A3A3A",
    shadowOpacity: 0,
    elevation: 0,
  },
  runButtonRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  runButtonText: {
    color: tokens.colors.ink_soft,
    fontSize: 15,
    fontWeight: "700",
    letterSpacing: 1.5,
    textTransform: "uppercase",
  },
  outputBlock: {
    marginTop: tokens.spacing.lg,
    padding: tokens.spacing.md,
    backgroundColor: tokens.colors.panel_fill,
    borderLeftColor: tokens.colors.copper_reveal,
    borderLeftWidth: 4,
    borderRadius: tokens.radius.md,
    gap: tokens.spacing.sm,
  },
  outputLabel: {
    fontSize: 10,
    color: tokens.colors.copper_reveal,
    letterSpacing: 2,
  },
  outputText: {
    color: tokens.colors.accent_amber,
    fontSize: 14,
    lineHeight: 22,
  },
  outputMeta: {
    color: tokens.colors.ink_muted,
    fontSize: 11,
    marginTop: tokens.spacing.sm,
  },
  errorBlock: {
    marginTop: tokens.spacing.md,
    padding: tokens.spacing.md,
    borderColor: tokens.colors.error,
    borderWidth: 1,
    borderRadius: tokens.radius.md,
    backgroundColor: "rgba(239,68,68,0.12)",
  },
  errorLabel: {
    fontSize: 10,
    letterSpacing: 2,
    color: tokens.colors.error,
  },
  errorText: {
    color: tokens.colors.ink_soft,
    marginTop: 6,
  },
  footer: {
    marginTop: tokens.spacing.xl,
    paddingTop: tokens.spacing.md,
    borderTopColor: "rgba(44,62,80,0.5)",
    borderTopWidth: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  footerText: {
    fontSize: 11,
    color: "#566575",
    letterSpacing: 1.2,
  },
  footerDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: tokens.colors.success,
  },
});
