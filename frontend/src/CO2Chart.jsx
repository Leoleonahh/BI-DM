import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";


export default function CO2Chart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="year" />
        <YAxis />

        <Tooltip />
        <Legend />

        <Line
          type="monotone"
          dataKey="actual"
          stroke="#2ecc71"
          name="Actual CO₂ (MtCO₂)"
        />

        <Line
          type="monotone"
          dataKey="predicted"
          stroke="#e74c3c"
          strokeDasharray="5 5"
          name="Predicted CO₂ (MtCO₂)"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}