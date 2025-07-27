import { Stack } from 'expo-router';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded] = useFonts({
    'SF-Pro-Display-Regular': require('../assets/fonts/SFProDisplay-Regular.otf'),
    'SF-Pro-Display-Medium': require('../assets/fonts/SFProDisplay-Medium.otf'),
    'SF-Pro-Display-Semibold': require('../assets/fonts/SFProDisplay-Semibold.otf'),
    'SF-Pro-Display-Bold': require('../assets/fonts/SFProDisplay-Bold.otf'),
  });

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="chat/[id]" options={{ headerShown: false }} />
    </Stack>
  );
}