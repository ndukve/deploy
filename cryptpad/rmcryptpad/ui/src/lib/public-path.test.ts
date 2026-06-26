import { expect, test } from "vitest";

import { cryptpadUiBasePath } from "./public-path";

test("builds the federated UI under the /ui/cryptpad/ mount point", () => {
  expect(cryptpadUiBasePath).toBe("/ui/cryptpad/");
});
