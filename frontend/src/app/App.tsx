import { FlaskConical, Hexagon, Microscope, MoveUpRight } from 'lucide-react';
import { ServiceStatus } from '../components/ServiceStatus';
import { WorkflowCard } from '../features/overview/WorkflowCard';

const workflows = [
  {
    id: '01',
    index: '01 / MOTION',
    name: 'Ultrasound tracking',
    modality: 'ULTRASOUND',
    description: 'Frame-to-frame object tracking research for dynamic ultrasound sequences.',
    method: 'Temporal tracking',
    icon: Microscope,
    motif: 'wave' as const,
  },
  {
    id: '02',
    index: '02 / STRUCTURE',
    name: 'Brain MRI segmentation',
    modality: 'MAGNETIC RESONANCE',
    description: 'A planned workspace for exploring image segmentation on brain MRI studies.',
    method: 'Volumetric segmentation',
    icon: FlaskConical,
    motif: 'brain' as const,
  },
  {
    id: '03',
    index: '03 / DETECTION',
    name: 'Lung CT candidates',
    modality: 'COMPUTED TOMOGRAPHY',
    description: 'A planned candidate-detection workflow for research with lung CT imagery.',
    method: 'Candidate localization',
    icon: Hexagon,
    motif: 'scan' as const,
  },
];

export default function App() {
  return (
    <main className="min-h-[100dvh] bg-[#edf2ec]">
      <div className="mx-auto max-w-[1440px] px-5 sm:px-9 lg:px-[72px]">
        <header className="flex h-[76px] items-center justify-between border-b border-[#d4dfd6]">
          <a href="/" className="flex items-center gap-3" aria-label="MedVision AI Lab overview">
            <span className="grid h-9 w-9 place-items-center rounded-[11px] bg-[#173d37] text-[#d5eb80]">
              <span className="relative block h-[17px] w-[17px]">
                <span className="absolute left-[7px] top-0 h-[17px] w-[3px] rounded-full bg-current" />
                <span className="absolute left-0 top-[7px] h-[3px] w-[17px] rounded-full bg-current" />
              </span>
            </span>
            <span>
              <span className="block text-[13px] font-extrabold tracking-[-.03em] text-[#193a35]">MedVision <span className="font-medium">AI Lab</span></span>
              <span className="eyebrow mt-0.5 block text-[8px] text-[#71837b]">Research imaging workstation</span>
            </span>
          </a>
          <div className="hidden items-center gap-2 sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-[#d0e875]" />
            <span className="eyebrow text-[#647970]">Foundation build · 01</span>
          </div>
          <span className="mono text-[10px] text-[#71837b] sm:hidden">PHASE 01</span>
        </header>

        <section className="grid gap-9 pb-10 pt-10 md:grid-cols-[1.25fr_.75fr] md:items-end md:gap-12 md:pb-12 md:pt-[62px]">
          <div className="enter">
            <p className="eyebrow mb-5 flex items-center gap-2 text-[#168b7a]"><span className="h-px w-6 bg-[#168b7a]" /> An open lab for image analysis</p>
            <h1 className="max-w-[770px] text-[clamp(42px,6.5vw,82px)] font-semibold leading-[.99] tracking-[-.075em] text-[#173d37]">
              See the signal.<br /><span className="font-medium text-[#6a8378]">Study the image.</span>
            </h1>
            <p className="mt-6 max-w-[490px] text-[15px] leading-[1.8] text-[#5f756b]">
              A research workstation taking shape around medical imaging experiments. Three workflows are on the roadmap; none are available yet.
            </p>
          </div>

          <div className="mesh-panel relative min-h-[226px] overflow-hidden rounded-[4px] p-6 text-[#e2efe2] md:min-h-[252px] md:p-7 enter-delay">
            <div className="relative z-10 flex items-start justify-between">
              <div>
                <p className="eyebrow text-[#acd1b9]">Workspace overview</p>
                <p className="mt-2 text-[13px] text-[#d0e2d5]">A considered starting point.</p>
              </div>
              <MoveUpRight size={17} className="text-[#d5e978]" />
            </div>
            <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between md:bottom-7 md:left-7 md:right-7">
              <div>
                <p className="eyebrow text-[#a8c7b2]">Research pipelines</p>
                <p className="mt-1 text-[53px] font-semibold leading-none tracking-[-.07em] text-[#eff3d7]">03<span className="ml-2 text-[18px] font-medium tracking-normal text-[#b2cbb6]">planned</span></p>
              </div>
              <div className="mb-1 h-[58px] w-[58px] rounded-full border border-[#89b7a0]/50 p-2">
                <div className="grid h-full w-full place-items-center rounded-full border border-[#89b7a0]/60 text-[#d5e978]">
                  <Microscope size={21} strokeWidth={1.3} />
                </div>
              </div>
            </div>
            <div className="absolute -right-8 top-[42%] h-28 w-28 rounded-full border border-[#9fc7ab]/20" />
            <div className="absolute -right-2 top-[46%] h-16 w-16 rounded-full border border-[#9fc7ab]/25" />
          </div>
        </section>

        <ServiceStatus />

        <section className="pb-16 pt-10 md:pb-20 md:pt-[54px]">
          <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <p className="eyebrow mb-2 text-[#168b7a]">The research map</p>
              <h2 className="text-[29px] font-semibold tracking-[-.055em] text-[#193a35]">Workflows in scope</h2>
            </div>
            <p className="max-w-[300px] text-[12px] leading-[1.65] text-[#71837b]">An honest preview of the lab’s planned areas of exploration.</p>
          </div>
          <div className="grid gap-x-7 gap-y-10 md:grid-cols-3">
            {workflows.map((workflow) => <WorkflowCard key={workflow.id} workflow={workflow} />)}
          </div>
        </section>

        <footer className="flex flex-col gap-4 border-t border-[#d4dfd6] py-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="eyebrow text-[#788980]">MedVision AI Lab <span className="px-1 text-[#a5b2a8]">/</span> Phase one foundation</p>
          <p className="max-w-[640px] text-[11px] leading-relaxed text-[#74857c]">
            For research and educational use only. This project is not a medical device and is not intended for diagnosis, treatment, or clinical decision-making.
          </p>
        </footer>
      </div>
    </main>
  );
}