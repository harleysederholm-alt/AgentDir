import { useEffect, useRef } from "react";
import { Animated, Easing, StyleSheet, Text, View } from "react-native";
import { tokens } from "../theme";

export type AchiiStatus = "IDLE" | "PROCESSING" | "SUCCESS" | "ERROR";

interface Props {
  status: AchiiStatus;
}

const LABEL: Record<AchiiStatus, string> = {
  IDLE: "valmiustila",
  PROCESSING: "NPU-pulssi käynnissä",
  SUCCESS: "valjas valmis",
  ERROR: "valjasvirhe",
};

const RING_COLOR: Record<AchiiStatus, string> = {
  IDLE: tokens.colors.accent_amber,
  PROCESSING: tokens.colors.accent_amber,
  SUCCESS: tokens.colors.success,
  ERROR: tokens.colors.error,
};

/**
 * Achiin ylävartalo puhelimessa — yksi pyörivä kehä + kaksi silmää.
 * `PROCESSING`-tilassa kehä pulssittaa amber-väriä; muissa tiloissa
 * animaatio on täysin pysähtyneenä. Vrt. desktop AchiiCanvas: haluamme
 * saman "event-driven, no infinite loops" -käytöksen.
 */
export function AchiiStatusIndicator({ status }: Props) {
  const pulse = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    pulse.stopAnimation();
    if (status !== "PROCESSING") {
      pulse.setValue(0);
      return;
    }
    // Pulssi pyörii vain PROCESSING-tilan ajan — palautuu kokonaan kun
    // tila vaihtuu. Tämä ei ole UI-tason "decorative loop", vaan suora
    // signaali siitä että NPU on töissä.
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, {
          toValue: 1,
          duration: 1100,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulse, {
          toValue: 0,
          duration: 1100,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ]),
    );
    animation.start();
    return () => {
      animation.stop();
    };
  }, [status, pulse]);

  const ringScale = pulse.interpolate({
    inputRange: [0, 1],
    outputRange: [1, 1.12],
  });
  const ringOpacity = pulse.interpolate({
    inputRange: [0, 1],
    outputRange: [0.85, 0.35],
  });

  const ringColor = RING_COLOR[status];

  return (
    <View style={styles.wrap}>
      <Animated.View
        style={[
          styles.pulseRing,
          {
            borderColor: ringColor,
            transform: [{ scale: ringScale }],
            opacity: status === "PROCESSING" ? ringOpacity : 0.25,
          },
        ]}
      />
      <View style={[styles.core, status === "ERROR" && styles.coreError]}>
        <View style={styles.faceRow}>
          <View style={[styles.eye, { backgroundColor: ringColor }]} />
          <View style={[styles.eye, { backgroundColor: ringColor }]} />
        </View>
        <Text style={styles.coreLabel}>{LABEL[status]}</Text>
      </View>
    </View>
  );
}

const SIZE = 180;

const styles = StyleSheet.create({
  wrap: {
    width: SIZE,
    height: SIZE,
    alignItems: "center",
    justifyContent: "center",
  },
  pulseRing: {
    position: "absolute",
    width: SIZE,
    height: SIZE,
    borderRadius: SIZE / 2,
    borderWidth: 3,
  },
  core: {
    width: SIZE - 24,
    height: SIZE - 24,
    borderRadius: (SIZE - 24) / 2,
    backgroundColor: tokens.colors.panel_fill,
    borderColor: tokens.colors.panel_oxidized,
    borderWidth: 3,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOpacity: 0.6,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 20,
    elevation: 8,
  },
  coreError: {
    borderColor: tokens.colors.error,
  },
  faceRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 22,
    marginBottom: 14,
  },
  eye: {
    width: 14,
    height: 14,
    borderRadius: 7,
    shadowColor: tokens.colors.accent_amber,
    shadowOpacity: 0.85,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 0 },
  },
  coreLabel: {
    fontSize: 11,
    letterSpacing: 2,
    textTransform: "uppercase",
    color: tokens.colors.ink_muted,
  },
});
