import { useParams } from "@tanstack/react-router";

import { WindowsPhase1 } from "../instructions/windows/WindowsPhase1";
import { WindowsPhase2 } from "../instructions/windows/WindowsPhase2";
import { WindowsPhase3 } from "../instructions/windows/WindowsPhase3";
import { WindowsPhase4 } from "../instructions/windows/WindowsPhase4";

const PHASE_MAP: Record<string, React.ComponentType> = {
  1: WindowsPhase1,
  2: WindowsPhase2,
  3: WindowsPhase3,
  4: WindowsPhase4,
};

export const WindowsPhasePage = () => {
  const { phaseId }: { phaseId: string } = useParams({
    // @ts-expect-error route is not in the standalone-mode router tree
    from: "/windows/$phaseId",
  });
  const PhaseComponent = PHASE_MAP[phaseId];

  if (!PhaseComponent) return <div>Invalid phase: {phaseId}</div>;

  return (
    <div className="max-w-5xl">
      <PhaseComponent />
    </div>
  );
};
