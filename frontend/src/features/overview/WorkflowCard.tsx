import { ArrowUpRight } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface Workflow {
  id: string;
  index: string;
  name: string;
  modality: string;
  description: string;
  method: string;
  icon: LucideIcon;
  motif: 'wave' | 'brain' | 'scan';
}

function ModalityIllustration({ motif }: { motif: Workflow['motif'] }) {
  return (
    <div className={`relative flex h-[134px] items-center justify-center overflow-hidden rounded-[4px] bg-[#e6eee6] modality-${motif}`} aria-hidden="true">
      <div className="scan-frame">
        {motif === 'wave' && (
          <svg viewBox="0 0 240 100" className="h-[100px] w-full">
            <path d="M2 51h33l9-5 8 14 14-35 13 59 14-43 10 20h20l8-8 7 12 12-29 12 38 11-23 10 4h25" fill="none" stroke="#188b7b" strokeWidth="2" />
            <path d="M2 51h33l9-5 8 14 14-35 13 59 14-43 10 20h20l8-8 7 12 12-29 12 38 11-23 10 4h25" fill="none" stroke="#188b7b" strokeWidth="8" opacity=".08" />
            <path d="M0 25h240M0 75h240" stroke="#7ca499" strokeDasharray="2 5" opacity=".5" />
          </svg>
        )}
        {motif === 'brain' && (
          <svg viewBox="0 0 180 120" className="h-[112px] w-[180px]">
            <ellipse cx="90" cy="60" rx="62" ry="45" fill="#d3e2d8" stroke="#4d8d7e" strokeWidth="1.5" />
            <ellipse cx="90" cy="60" rx="48" ry="34" fill="none" stroke="#7cac9e" strokeWidth="1" />
            <path d="M87 18c-8 13 1 20-5 29s-17 5-17 17 16 11 12 25M94 18c8 11-2 19 6 26s18 6 15 17-15 12-9 29M44 48c16 5 18-5 27-10m-27 38c17-5 20 2 32 8m58-35c-15 3-17-5-28-10m28 39c-14-6-17 2-29 8" fill="none" stroke="#248d7b" strokeWidth="1.5" />
            <circle cx="89" cy="60" r="4" fill="#d0e875" />
          </svg>
        )}
        {motif === 'scan' && (
          <svg viewBox="0 0 180 120" className="h-[112px] w-[180px]">
            <ellipse cx="90" cy="60" rx="60" ry="42" fill="#d2e1d8" stroke="#4d8d7e" />
            <ellipse cx="90" cy="60" rx="47" ry="31" fill="#bcd2c6" stroke="#79a596" />
            <path d="M54 56c7-13 17-13 24-4 8 11 15 9 22 1 9-10 19-7 27 4m-74 13c9-5 16-3 23 3s15 6 22 0 15-7 25 0" fill="none" stroke="#668f82" strokeWidth="2" />
            <circle cx="107" cy="53" r="8" fill="none" stroke="#be6650" strokeWidth="2" />
            <path d="M107 40v26m-13-13h26" stroke="#be6650" strokeWidth="1" opacity=".7" />
          </svg>
        )}
      </div>
      <span className="eyebrow absolute bottom-3 left-3 text-[#68867c]">IMAGING STUDY · PREVIEW</span>
      <span className="absolute right-3 top-3 h-1.5 w-1.5 rounded-full bg-[#168b7a]" />
    </div>
  );
}

export function WorkflowCard({ workflow }: { workflow: Workflow }) {
  const Icon = workflow.icon;
  return (
    <article className="group border-t border-[#b9cbc0] pt-5">
      <div className="mb-4 flex items-center justify-between">
        <span className="eyebrow text-[#75877f]">{workflow.index}</span>
        <span className="flex items-center gap-1.5 rounded-full bg-[#e2e9df] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[.08em] text-[#63776e]">
          <span className="h-1.5 w-1.5 rounded-full bg-[#a0ada3]" />
          Planned
        </span>
      </div>
      <ModalityIllustration motif={workflow.motif} />
      <div className="flex items-start justify-between gap-3 pt-5">
        <div>
          <p className="eyebrow mb-2 text-[#168b7a]">{workflow.modality}</p>
          <h3 className="text-[19px] font-extrabold leading-tight tracking-[-.04em] text-[#193a35]">{workflow.name}</h3>
        </div>
        <span className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-full border border-[#d4dfd6] text-[#557169]">
          <Icon size={15} strokeWidth={1.7} />
        </span>
      </div>
      <p className="mt-3 min-h-[42px] text-[13px] leading-[1.65] text-[#647970]">{workflow.description}</p>
      <div className="mt-5 flex items-center justify-between border-t border-[#d8e1d9] pt-3.5">
        <span className="mono text-[10px] text-[#71847a]">{workflow.method}</span>
        <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-[.12em] text-[#76877e]">
          Not yet implemented <ArrowUpRight size={12} />
        </span>
      </div>
    </article>
  );
}