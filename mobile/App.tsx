import { StatusBar } from "expo-status-bar";
import { SafeAreaView, StyleSheet } from "react-native";
import { AchiiMobileApp } from "./src/AchiiMobileApp";
import { tokens } from "./src/theme";

export default function App() {
  return (
    <SafeAreaView style={styles.root}>
      <StatusBar style="light" backgroundColor={tokens.colors.base_bg} />
      <AchiiMobileApp />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: tokens.colors.base_bg,
  },
});
