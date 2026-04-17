import * as Haptics from "expo-haptics";
import { Platform, Vibration } from "react-native";

/**
 * Haptic playbook — mapattu pitch-deckin kuvaukseen:
 *
 *  - `mechanicalClick` = "BZZZ klik mekaaninen"  → nopea kaksoispulssi.
 *    Triggered when the user presses the Run-Local-Harness button.
 *
 *  - `mechanicalDing`  = "BZZT mekaaninen ding"  → yksi jämäkkä pulssi.
 *    Triggered when inference completes.
 *
 * Expo Haptics is used on native (iOS/Android) because it maps to the
 * OS-level Taptic / vibrator APIs. On web we fall back to
 * `navigator.vibrate` with the exact pattern documented in the PRD
 * (`[10, 30, 10]` / `50`).
 */

export async function mechanicalClick(): Promise<void> {
  if (Platform.OS === "web") {
    if (typeof window !== "undefined" && "vibrate" in window.navigator) {
      window.navigator.vibrate([10, 30, 10]);
    }
    return;
  }
  try {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    // Small delay to produce the "klik-klak" mechanical doublet.
    await new Promise((r) => setTimeout(r, 35));
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  } catch {
    Vibration.vibrate([10, 30, 10] as unknown as number[]);
  }
}

export async function mechanicalDing(): Promise<void> {
  if (Platform.OS === "web") {
    if (typeof window !== "undefined" && "vibrate" in window.navigator) {
      window.navigator.vibrate(50);
    }
    return;
  }
  try {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  } catch {
    Vibration.vibrate(50);
  }
}

export async function mechanicalError(): Promise<void> {
  if (Platform.OS === "web") {
    if (typeof window !== "undefined" && "vibrate" in window.navigator) {
      window.navigator.vibrate([20, 40, 20, 40, 20]);
    }
    return;
  }
  try {
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
  } catch {
    Vibration.vibrate([20, 40, 20, 40, 20]);
  }
}
