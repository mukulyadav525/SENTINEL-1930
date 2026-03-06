import {
    PhoneIncoming,
    ShieldCheck,
    ShieldAlert,
    MessageSquare,
    Users,
    IndianRupee,
    AlertTriangle,
    PhoneOff
} from "lucide-react";

export const initialCalls = [
    { id: 1, number: "+91 98XXX X1234", location: "Mumbai, MH", score: 0.12, status: "Safe", time: "Just now" },
    { id: 2, number: "+91 90000 X5678", location: "Overseas (Spoofed)", score: 0.89, status: "Scam", time: "1 min ago" },
    { id: 3, number: "+91 82XXX X9012", location: "Bangalore, KA", score: 0.45, status: "Suspicious", time: "3 mins ago" },
    { id: 4, number: "+91 98XXX X3456", location: "Delhi, DL", score: 0.05, status: "Safe", time: "5 mins ago" },
];

export const personas = [
    { id: 1, name: "Elderly Uncle", language: "Hindi/English", traits: "Confused, Patient", active: true },
    { id: 2, name: "Busy Executive", language: "English", traits: "Hurried, Skeptical", active: false },
    { id: 3, name: "Rural Farmer", language: "Marathi", traits: "Trusting, Traditional", active: false },
];

export const activeSessions = [
    { id: "S-101", caller: "+91 91234 XXXXX", persona: "Elderly Uncle", duration: "12m 40s", status: "Engaged", script: "KYC Verification Trap" },
    { id: "S-102", caller: "+91 88776 XXXXX", persona: "Busy Executive", duration: "04m 15s", status: "Fatiguing", script: "Bank Loan Offer" },
];

export const recentBroadcasts = [
    { time: "1h ago", status: "Delivered", title: "UPI Scam Surge" },
    { time: "4h ago", status: "Delivered", title: "Fake Job Ad Alert" },
];

export const riskVectors = [
    { name: "Bulk Dialing Pattern", value: 34 },
    { name: "Spoofed CLI Detected", value: 28 },
    { name: "High-Risk VOIP Range", value: 21 },
    { name: "SIM-Swap Anomaly", value: 17 }
];

export const liveFeedItems = [1, 2, 3, 4].map((i) => ({
    id: i,
    location: "Delhi-NCR Surge",
    message: 'AI Honeypot intercepted a "KYC Update" scam targeting senior citizens.',
    time: "2 mins ago • SID-193022"
}));
