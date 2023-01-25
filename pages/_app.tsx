import React from "react";
import { AppProps } from "next/app";
import { Refine } from "@pankod/refine-core";
import {
  NotificationsProvider,
  notificationProvider,
  MantineProvider,
  Global,
  ReadyPage,
  ErrorComponent,
  useLocalStorage,
  ColorSchemeProvider,
  ColorScheme,
  DarkTheme,
  LightTheme,
} from "@pankod/refine-mantine";
import routerProvider from "@pankod/refine-nextjs-router";
import dataProvider from "@pankod/refine-simple-rest";
import { MantineInferencer } from "@pankod/refine-inferencer/mantine";
import { Title, Sider, Layout, Header } from "@components/layout";

const API_URL = "https://api.fake-rest.refine.dev";

function MyApp({ Component, pageProps }: AppProps): JSX.Element {
  const [colorScheme, setColorScheme] = useLocalStorage<ColorScheme>({
    key: "mantine-color-scheme",
    defaultValue: "light",
    getInitialValueInEffect: true,
  });
  const toggleColorScheme = (value?: ColorScheme) =>
    setColorScheme(value || (colorScheme === "dark" ? "light" : "dark"));
  return (
    <ColorSchemeProvider
      colorScheme={colorScheme}
      toggleColorScheme={toggleColorScheme}
    >
      <MantineProvider
        theme={colorScheme === "dark" ? DarkTheme : LightTheme}
        withNormalizeCSS
        withGlobalStyles
      >
        <Global styles={{ body: { WebkitFontSmoothing: "auto" } }} />
        <NotificationsProvider position="top-right">
          <Refine
            routerProvider={routerProvider}
            dataProvider={dataProvider(API_URL)}
            notificationProvider={notificationProvider}
            ReadyPage={ReadyPage}
            catchAll={<ErrorComponent />}
            resources={[
              {
                name: "posts",
                list: MantineInferencer,
                edit: MantineInferencer,
                show: MantineInferencer,
                create: MantineInferencer,
                canDelete: true,
              },
            ]}
            Title={Title}
            Sider={Sider}
            Layout={Layout}
            Header={Header}
          >
            <Component {...pageProps} />
          </Refine>
        </NotificationsProvider>
      </MantineProvider>
    </ColorSchemeProvider>
  );
}

export default MyApp;
