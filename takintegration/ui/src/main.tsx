import {
  Outlet,
  RouterProvider,
  createRouter,
  createRootRoute,
  createRoute,
  redirect,
} from "@tanstack/react-router";
import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./i18n";

const rootRoute = createRootRoute({
  component: () => (
    <>
      <Outlet />
    </>
  ),
});

const mtxRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "product/tak/$",
  component: () => {
    const SAMPLE_DATA = {
      data: {},
    };

    // @ts-expect-error App's data prop typing isn't satisfied by the empty stand-alone sample
    return <App data={SAMPLE_DATA.data} />;
  },
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    throw redirect({
      // @ts-expect-error standalone target path isn't in the typed route tree
      to: "/product/tak",
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
  import("./index.css");
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
