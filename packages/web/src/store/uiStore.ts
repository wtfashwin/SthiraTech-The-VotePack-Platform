/**
 * Zustand store for UI state management.
 * This store ONLY contains UI-specific state (not server data).
 */
import { create } from 'zustand';

interface UiStore {
  // Active trip ID (for navigation context)
  activeTripId: string | null;
  setActiveTripId: (tripId: string | null) => void;

  // Modal visibility states
  isAddParticipantModalOpen: boolean;
  setAddParticipantModalOpen: (isOpen: boolean) => void;

  isAddDayModalOpen: boolean;
  setAddDayModalOpen: (isOpen: boolean) => void;

  isAddActivityModalOpen: boolean;
  setAddActivityModalOpen: (isOpen: boolean) => void;

  isCreatePollModalOpen: boolean;
  setCreatePollModalOpen: (isOpen: boolean) => void;

  isAddExpenseModalOpen: boolean;
  setAddExpenseModalOpen: (isOpen: boolean) => void;

  isImportUrlModalOpen: boolean;
  setImportUrlModalOpen: (isOpen: boolean) => void;

  isCommitmentModalOpen: boolean;
  setCommitmentModalOpen: (isOpen: boolean) => void;

  // Selected day ID (for adding activities)
  selectedDayId: string | null;
  setSelectedDayId: (dayId: string | null) => void;
}

export const useUiStore = create<UiStore>((set) => ({
  // Initial state
  activeTripId: null,
  setActiveTripId: (tripId) => set({ activeTripId: tripId }),

  isAddParticipantModalOpen: false,
  setAddParticipantModalOpen: (isOpen) => set({ isAddParticipantModalOpen: isOpen }),

  isAddDayModalOpen: false,
  setAddDayModalOpen: (isOpen) => set({ isAddDayModalOpen: isOpen }),

  isAddActivityModalOpen: false,
  setAddActivityModalOpen: (isOpen) => set({ isAddActivityModalOpen: isOpen }),

  isCreatePollModalOpen: false,
  setCreatePollModalOpen: (isOpen) => set({ isCreatePollModalOpen: isOpen }),

  isAddExpenseModalOpen: false,
  setAddExpenseModalOpen: (isOpen) => set({ isAddExpenseModalOpen: isOpen }),

  isImportUrlModalOpen: false,
  setImportUrlModalOpen: (isOpen) => set({ isImportUrlModalOpen: isOpen }),

  isCommitmentModalOpen: false,
  setCommitmentModalOpen: (isOpen) => set({ isCommitmentModalOpen: isOpen }),

  selectedDayId: null,
  setSelectedDayId: (dayId) => set({ selectedDayId: dayId }),
}));
