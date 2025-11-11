import React, { useEffect, useMemo, useState } from "react";
import { getExpenses, createExpense, updateExpense, deleteExpense } from "../api";
import {
    Box,
    Button,
    Typography,
    Paper,
    Table,
    TableHead,
    TableRow,
    TableCell,
    TableBody,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Stack,
    Snackbar,
    Alert,
    CircularProgress,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

const CATEGORIES = [
    "Food",
    "Transport",
    "Entertainment",
    "Shopping",
    "Bills",
    "Health",
    "Other",
];

function formatDisplayDate(value) {
    try {
        const d = new Date(value);
        if (Number.isNaN(d.getTime())) return "-";
        return d.toLocaleDateString();
    } catch {
        return "-";
    }
}

function toISODate(dateStr) {
    if (!dateStr) return undefined;
    return `${dateStr}T00:00:00Z`;
}

function toInputDate(value) {
    if (!value) return "";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return "";
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd}`;
}

export default function Spending() {
    const [expenses, setExpenses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [mode, setMode] = useState("create");
    const [editingId, setEditingId] = useState(null);

    const [category, setCategory] = useState("");
    const [amount, setAmount] = useState("");
    const [date, setDate] = useState("");

    const token = useMemo(() => localStorage.getItem("token"), []);

    const loadExpenses = async () => {
        if (!token) {
        setError("Please login to view expenses.");
        setLoading(false);
        return;
        }
        setError("");
        setLoading(true);
        try {
        const data = await getExpenses(token);
        setExpenses(Array.isArray(data) ? data : []);
        } catch (e) {
        setError(e.message || "Failed to load expenses");
        } finally {
        setLoading(false);
        }
    };

    useEffect(() => {
        loadExpenses();

    }, []);

    const openAddModal = () => {
        setMode("create");
        setEditingId(null);
        setCategory("");
        setAmount("");
        setDate("");
        setIsModalOpen(true);
    };

    const openEditModal = (exp) => {
        setMode("edit");
        setEditingId(exp.id);
        setCategory(exp.category || "");
        setAmount(String(exp.amount ?? ""));
        setDate(toInputDate(exp.date));
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!token) {
        setError("Not authenticated");
        return;
        }
        const payload = {
        category,
        amount: amount ? Number(amount) : undefined,
        date: toISODate(date),
        };
        try {
        if (mode === "create") {
            await createExpense(token, payload);
        } else if (mode === "edit" && editingId != null) {
            await updateExpense(token, editingId, payload);
        }
        closeModal();
        await loadExpenses();
        } catch (e) {
        setError(e.message || "Failed to save expense");
        }
    };

    const handleDelete = async (id) => {
        if (!token) return;
        const ok = window.confirm("Delete this expense?");
        if (!ok) return;
        try {
        await deleteExpense(token, id);
        setExpenses((prev) => prev.filter((x) => x.id !== id));
        } catch (e) {
        setError(e.message || "Failed to delete expense");
        }
    };

    return (
        <Box p={3}>
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h5">Spending</Typography>
            <Button variant="contained" onClick={openAddModal}>+ Add Expense</Button>
        </Stack>

        {loading ? (
            <Stack direction="row" alignItems="center" spacing={1}>
            <CircularProgress size={20} />
            <Typography variant="body2">Loading expenses...</Typography>
            </Stack>
        ) : (
            <Paper>
            <Table size="small">
                <TableHead>
                <TableRow>
                    <TableCell>Category</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Actions</TableCell>
                </TableRow>
                </TableHead>
                <TableBody>
                {expenses.length === 0 ? (
                    <TableRow>
                    <TableCell colSpan={4}>
                        <Typography color="text.secondary">No expenses found</Typography>
                    </TableCell>
                    </TableRow>
                ) : (
                    expenses.map((exp) => (
                    <TableRow key={exp.id} hover>
                        <TableCell>{exp.category}</TableCell>
                        <TableCell>${Number(exp.amount).toFixed(2)}</TableCell>
                        <TableCell>{formatDisplayDate(exp.date)}</TableCell>
                        <TableCell>
                        <IconButton aria-label="edit" onClick={() => openEditModal(exp)} size="small">
                            <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton aria-label="delete" color="error" onClick={() => handleDelete(exp.id)} size="small">
                            <DeleteIcon fontSize="small" />
                        </IconButton>
                        </TableCell>
                    </TableRow>
                    ))
                )}
                </TableBody>
            </Table>
            </Paper>
        )}

        <Dialog open={isModalOpen} onClose={closeModal} fullWidth maxWidth="xs">
            <DialogTitle>{mode === "create" ? "Add Expense" : "Edit Expense"}</DialogTitle>
            <DialogContent>
            <Box component="form" id="expense-form" onSubmit={handleSubmit}>
                <FormControl fullWidth margin="normal">
                <InputLabel id="category-label">Category</InputLabel>
                <Select
                    labelId="category-label"
                    label="Category"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    required
                >
                    {CATEGORIES.map((c) => (
                    <MenuItem key={c} value={c}>
                        {c}
                    </MenuItem>
                    ))}
                </Select>
                </FormControl>

                <TextField
                label="Amount"
                type="number"
                inputProps={{ min: 0.01, step: 0.01 }}
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
                fullWidth
                margin="normal"
                />

                <TextField
                label="Date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                fullWidth
                margin="normal"
                InputLabelProps={{ shrink: true }}
                />
            </Box>
            </DialogContent>
            <DialogActions>
            <Button onClick={closeModal}>Cancel</Button>
            <Button form="expense-form" type="submit" variant="contained">
                {mode === "create" ? "Add" : "Save"}
            </Button>
            </DialogActions>
        </Dialog>

        <Snackbar
            open={Boolean(error)}
            autoHideDuration={4000}
            onClose={() => setError("")}
            anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
            <Alert onClose={() => setError("")} severity="error" variant="filled" sx={{ width: "100%" }}>
            {error}
            </Alert>
        </Snackbar>
        </Box>
    );
}

