import { PRODUCT_SHORTNAME } from "@/App";
import { JSX, HTMLAttributes } from "react";
import { useTranslation } from "react-i18next";

type TranslatedTextProps = {
  id: string;
} & HTMLAttributes<HTMLSpanElement>;

export function TranslatedText({
  id,
  ...props
}: TranslatedTextProps): JSX.Element {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  return <span {...props}>{t(id)}</span>;
}
