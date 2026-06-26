import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  RouterProvider,
} from "@tanstack/react-router";

import { HomePage } from "./pages/HomePage";

import enLang from "./locales/en.json";
import fiLang from "./locales/fi.json";
import svLang from "./locales/sv.json";
import { MetaData, MetaProvider, CryptPadCardData } from "./lib/metadata";

export const PRODUCT_SHORTNAME = "cryptpad";

function RootLayoutComponent() {
  return (
    <div className="max-w-5xl mx-auto p-6">
      <Outlet />
    </div>
  );
}

interface Props {
  data: CryptPadCardData;
  meta: MetaData;
}

export default function CryptPadApp({ data, meta }: Props) {
  const [ready, setReady] = useState(false);
  const { i18n } = useTranslation(PRODUCT_SHORTNAME);

  const rootRoute = useMemo(
    () =>
      createRootRoute({
        component: RootLayoutComponent,
      }),
    [],
  );

  const homeRoute = useMemo(
    () =>
      createRoute({
        getParentRoute: () => rootRoute,
        path: "/",
        component: () => <HomePage data={data} />,
      }),
    [rootRoute, data],
  );

  const routeTree = useMemo(
    () => rootRoute.addChildren([homeRoute]),
    [rootRoute, homeRoute],
  );

  const router = useMemo(
    () => createRouter({ routeTree, basepath: "/product/cryptpad" }),
    [routeTree],
  );

  useEffect(() => {
    async function load() {
      i18n.addResourceBundle("en", PRODUCT_SHORTNAME, enLang);
      i18n.addResourceBundle("fi", PRODUCT_SHORTNAME, fiLang);
      i18n.addResourceBundle("sv", PRODUCT_SHORTNAME, svLang);

      await i18n.loadNamespaces(PRODUCT_SHORTNAME);
      setReady(true);
    }

    void load();
  }, [i18n]);

  if (!ready) return null;

  return (
    <MetaProvider meta={meta}>
      <RouterProvider router={router} />
    </MetaProvider>
  );
}
