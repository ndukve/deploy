import { expect, test } from "vitest";

test("PRODUCT_SHORTNAME is cryptpad", async () => {
  const { PRODUCT_SHORTNAME } = await import("./App");
  expect(PRODUCT_SHORTNAME).toBe("cryptpad");
});
