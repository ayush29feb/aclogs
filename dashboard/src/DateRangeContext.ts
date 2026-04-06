import { createContext, useContext } from 'react';

export type DateRange = { label: string; months: number | null };

export const DATE_RANGES: DateRange[] = [
  { label: '1M', months: 1 },
  { label: '3M', months: 3 },
  { label: '6M', months: 6 },
  { label: '1Y', months: 12 },
  { label: 'All', months: null },
];

export function sinceDate(months: number): string {
  const d = new Date();
  d.setMonth(d.getMonth() - months);
  return d.toISOString().slice(0, 10);
}

export type DateRangeContextValue = {
  range: number | null;
  setRange: (months: number | null) => void;
  since: string | null;
};

export const DateRangeContext = createContext<DateRangeContextValue>({
  range: null,
  setRange: () => {},
  since: null,
});

export function useDateRange() {
  return useContext(DateRangeContext);
}
