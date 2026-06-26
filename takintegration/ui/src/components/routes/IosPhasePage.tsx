import { useParams } from "@tanstack/react-router";

import { IosPhase1 } from "../instructions/ios/IosPhase1";
import { IosPhase2 } from "../instructions/ios/IosPhase2";
import { IosPhase3 } from "../instructions/ios/IosPhase3";
import { IosPhase4 } from "../instructions/ios/IosPhase4";
import { IosPhase5 } from "../instructions/ios/IosPhase5";

const PHASE_MAP: Record<string, React.ComponentType> = {
  1: IosPhase1,
  2: IosPhase2,
  3: IosPhase3,
  4: IosPhase4,
  5: IosPhase5,
};

export const IosPhasePage = () => {
  const { phaseId }: { phaseId: string } = useParams({
    // @ts-expect-error route is not in the standalone-mode router tree
    from: "/ios/$phaseId",
  });
  const PhaseComponent = PHASE_MAP[phaseId];

  if (!PhaseComponent) return <div>Invalid phase: {phaseId}</div>;

  return (
    <div className="max-w-5xl">
      <PhaseComponent />
    </div>
  );
};
