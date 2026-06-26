import { Button } from "./ui/button";

interface Props extends React.ComponentProps<typeof Button> {
  text: string;
  data: string;
  filename: string;
}

export function ZipButton({ text, data, filename, ...other }: Props) {
  const handleDownload = () => {
    try {
      const link = document.createElement("a");
      link.href = data;
      link.download = filename;
      link.click();
    } catch (err) {
      console.error("Error downloading file:", err);
    }
  };

  return (
    <Button onClick={handleDownload} {...other}>
      {text}
    </Button>
  );
}
