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

const mtxRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "product/mtx/$",
  component: () => {
    const SAMPLE_DATA = { data: {} };
    // @ts-expect-error App meta prop is injected by the host at runtime
    return <App data={SAMPLE_DATA} />;
  },
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    // eslint-disable-next-line @typescript-eslint/only-throw-error
    throw redirect({
      // @ts-expect-error route not registered in dev router
      to: "/product/mtx",
    });
  },
  component: () => <h1>Redirecting...</h1>,
});

const routeTree = rootRoute.addChildren([mtxRoute, indexRoute]);

const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

if (__USE_GLOBAL_CSS__ == true) {
  void import("./index.css");
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
