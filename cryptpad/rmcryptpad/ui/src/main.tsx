import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./i18n";

import {
  Outlet,
  RouterProvider,
  createRouter,
  createRootRoute,
  createRoute,
  redirect,
} from "@tanstack/react-router";

const rootRoute = createRootRoute({
  component: () => (
    <>
      <Outlet />
    </>
  ),
});

const cryptpadRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "product/cryptpad/$",
  component: () => {
    const SAMPLE_DATA = {
      url: "https://mtls.cryptpad.localhost:8443",
      sandbox_url: "https://mtls.sandbox.cryptpad.localhost:8443",
    };
    return (
      <App
        data={SAMPLE_DATA}
        meta={{ callsign: "VIRTA-1", theme: "default" }}
      />
    );
  },
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    throw redirect({
      // @ts-expect-error: TanStack Router strict mode requires registered routes
      to: "/product/cryptpad",
    });
  },
  component: () => <h1>Redirecting...</h1>,
});

const routeTree = rootRoute.addChildren([cryptpadRoute, indexRoute]);

const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

if (__USE_GLOBAL_CSS__ == true) {
  import("./index.css");
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
