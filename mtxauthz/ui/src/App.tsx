import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  RouterProvider,
} from "@tanstack/react-router";

import { StreamGridPage } from "./pages/StreamGridPage";
import { VideoPage } from "./pages/VideoPage";

import enLang from "./locales/en.json";
import fiLang from "./locales/fi.json";
import svLang from "./locales/sv.json";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MetaData, MetaProvider } from "./lib/metadata";
import { BroadcastWizard } from "./components/BroadcastWizard";
import { OnboardingHandler } from "./components/OnboardingHandler";
import { Toaster } from "./components/ui/sonner";

const RootLayoutComponent = () => (
  <div>
    <Outlet />
    <OnboardingHandler />
    <Toaster position="top-center" />
  </div>
);

const rootRoute = createRootRoute({
  component: RootLayoutComponent,
});

const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: HomeWrapper,
});

const streamRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "$slug",
  component: StreamWrapper,
});

function HomeWrapper() {
  const [wizardOpen, setWizardOpen] = useState(false);

  return (
    <>
      <StreamGridPage onStartBroadcast={() => setWizardOpen(true)} />
      <BroadcastWizard open={wizardOpen} onOpenChange={setWizardOpen} />
    </>
  );
}

function StreamWrapper() {
  const { slug } = streamRoute.useParams();
  return <VideoPage streamSlug={slug ?? ""} />;
}

const routeTree = rootRoute.addChildren([homeRoute, streamRoute]);

interface Props {
  data: unknown;
  meta: MetaData;
}

export const PRODUCT_SHORTNAME = "mtx";

export default ({ meta }: Props) => {
  const [ready, setReady] = useState(false);
  const { i18n } = useTranslation(PRODUCT_SHORTNAME);

  const queryClient = useMemo(() => new QueryClient(), []);
  const router = useMemo(
    () => createRouter({ routeTree, basepath: "/product/mtx" }),
    [],
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

  if (!ready) {
    return (
      <div
        className="flex items-center justify-center py-16"
        role="status"
        aria-busy="true"
      >
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <MetaProvider meta={meta}>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </MetaProvider>
  );
};
