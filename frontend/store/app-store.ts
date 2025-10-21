import { create } from "zustand";
import { fetchCards } from "@/lib/api";
import type { Card } from "@/lib/validators";

interface AppState {
    cards: Card[];
    isLoading: boolean;
    error: string | null;
    fetchCards: (title?:string) => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
    cards: [],
    isLoading: false,
    error: null,
    fetchCards: async (title) => {
        set({ isLoading:true , error: null});
        try{
            const cards = await fetchCards(title);
            set({ cards, isLoading:false});
        }catch (error){
            set({ error: "Failed to fetch cards.", isLoading: false });
        }
    }
}))