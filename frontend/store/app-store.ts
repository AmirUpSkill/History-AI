import { create } from "zustand";
import { fetchCards, createCard } from "@/lib/api";
import type { Card, CreateCardFormData } from "@/lib/validators";

interface AppState {
    // --- For Card Fetching ---
    cards: Card[];
    isLoading: boolean;
    error: string | null;
    fetchCards: (title?:string) => Promise<void>;
    // --- For Add Card --- 
    isAddCardDialogOpen: boolean
    isCreatingCard: boolean
    createCardError: string | null 
    // --- Action for dialog management --- 
    openAddCardDialog: () => void 
    closeAddCardDialog: () => void
    // --- Action for creating a card --- 
    createNewCard: (formData: CreateCardFormData ) => Promise<boolean>;
    // --- Action for resetting the state after card creation ---
    resetCreateCardState: () => void;

}

export const useAppStore = create<AppState>((set, get) => ({
    cards: [],
    isLoading: false,
    error: null,
    // --- Fetch Cards ---
    fetchCards: async (title) => {
        set({ isLoading: true, error: null });
        try {
            const cards = await fetchCards(title);
            set({ cards, isLoading: false });
        } catch (error) {
            set({ error: "Failed to fetch cards.", isLoading: false });
        }
    },
    // --- Card Dialog State --- 
    isAddCardDialogOpen: false,
    isCreatingCard: false,
    createCardError: null,

    // --- Here List of Dialog Actions --- 
    // --- Open the "Add Card" dialog --- 
    openAddCardDialog: () => {
        set({
            isAddCardDialogOpen: true,
            createCardError: null,
        });
    },
    // --- Closes the "Add Card" dialog and reset --- 
    closeAddCardDialog: () => {
        set({
            isAddCardDialogOpen: false,
            createCardError: null,
            isCreatingCard: false,
        });
    },
    // --- Resets the creation Error --- 
    resetCreateCardState: () => {
        set({
            createCardError: null,
            isCreatingCard: false,
        });
    },
    // --- Create a new Card API --- 
    createNewCard: async (formData: CreateCardFormData) => {
        set({ isCreatingCard: true, createCardError: null });
        try {
            // --- Call the API to create the Card --- 
            const newCard = await createCard(formData);
            // --- Close dialog and refresh Cards --- 
            set({ isCreatingCard: false });
            get().closeAddCardDialog();
            // --- Refresh the Card List --- 
            await get().fetchCards();
            return true;
        } catch (error) {
            set({ createCardError: "Failed to create card.", isCreatingCard: false });
            return false;
        }
    },
}))
