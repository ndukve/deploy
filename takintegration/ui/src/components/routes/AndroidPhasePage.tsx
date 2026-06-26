import { useParams } from "@tanstack/react-router";

import { AndroidPhase1 } from "../instructions/android/AndroidPhase1";
import { AndroidPhase2 } from "../instructions/android/AndroidPhase2";
import { AndroidPhase3 } from "../instructions/android/AndroidPhase3";
import { AndroidPhase4 } from "../instructions/android/AndroidPhase4";
import { AndroidPhase5 } from "../instructions/android/AndroidPhase5";

const PHASE_MAP: Record<string, React.ComponentType> = {
  1: AndroidPhase1,
  2: AndroidPhase2,
  3: AndroidPhase3,
  4: AndroidPhase4,
  5: AndroidPhase5,
};

export const AndroidPhasePage = () => {
  const { phaseId }: { phaseId: string } = useParams({
    // @ts-expect-error route is not in the standalone-mode router tree
    from: "/android/$phaseId",
  });
  const PhaseComponent = PHASE_MAP[phaseId];

  if (!PhaseComponent) return <div>Invalid phase: {phaseId}</div>;

  return (
    <div className="max-w-5xl">
      <PhaseComponent />
    </div>
  );
};
