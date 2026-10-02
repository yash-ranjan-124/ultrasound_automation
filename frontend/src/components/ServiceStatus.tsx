import { Activity, RefreshCw, ShieldAlert } from 'lucide-react';
import { useHealthStatus } from '../hooks/use-health-status';

export function ServiceStatus() {
  const health = useHealthStatus();
  const isOnline = health.isSuccess;

  return (
    <section className="flex min-h-[92px] items-center justify-between gap-5 border-y border-[#d6e0d8] py-5" aria-label="Service status">
      <div className="flex items-center gap-3.5">
        <span className={`grid h-10 w-10 place-items-center rounded-full ${isOnline ? 'bg-[#d9eee4] text-[#168b7a]' : health.isError ? 'bg-[#f5e5df] text-[#a64d35]' : 'bg-[#e1e9e2] text-[#687c75]'}`}>
          {health.isError ? <ShieldAlert size={18} /> : <Activity size={18} />}
        </span>
        <div>
          <p className="eyebrow mb-1 text-[#687c75]">API connection</p>
          <p className="text-sm font-bold text-[#16312e]" role="status" aria-live="polite">
            {health.isPending && 'Checking service…'}
            {isOnline && 'Service online'}
            {health.isError && 'Service offline'}
          </p>
          {health.isError && <p className="mt-1 text-xs text-[#805e56]">The API did not respond. The overview remains available.</p>}
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="hidden text-right sm:block">
          <span className="eyebrow block text-[#687c75]">Endpoint</span>
          <span className="mono mt-1 block text-[11px] text-[#365851]">/api/v1/health</span>
        </span>
        {health.isError && (
          <button
            type="button"
            onClick={() => void health.refetch()}
            disabled={health.isFetching}
            className="inline-flex items-center gap-2 rounded-full border border-[#cddbd3] px-3.5 py-2 text-xs font-bold text-[#31564e] transition-colors hover:bg-[#e2ebe3] disabled:opacity-50"
          >
            <RefreshCw size={13} className={health.isFetching ? 'animate-spin' : ''} />
            Retry
          </button>
        )}
      </div>
    </section>
  );
}