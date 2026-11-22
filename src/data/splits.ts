// Trading date is in America/New_York. Only apply to pre-split snapshots.
export const splits: Record<string, { ratio: number; tradingDate: string; source: string }> = {
  SNDK: { ratio: 8, tradingDate: '2026-11-20', source: 'https://www.sec.gov/Archives/edgar/data/2023554/000162828026075127/sndk-20261119.htm' },
};
