"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"
import { TrendingUp, PieChartIcon, BarChart3, Calendar } from "lucide-react"

interface DataVisualizationProps {
  county: string
  score: number
}

export function DataVisualization({ county, score }: DataVisualizationProps) {
  // Mock historical resilience data
  const historicalData = [
    { month: "Jan", resilience: 72, rainfall: 45, temperature: 28 },
    { month: "Feb", resilience: 68, rainfall: 38, temperature: 30 },
    { month: "Mar", resilience: 65, rainfall: 42, temperature: 32 },
    { month: "Apr", resilience: 78, rainfall: 85, temperature: 29 },
    { month: "May", resilience: 82, rainfall: 120, temperature: 27 },
    { month: "Jun", resilience: 75, rainfall: 95, temperature: 25 },
    { month: "Jul", resilience: 70, rainfall: 65, temperature: 24 },
    { month: "Aug", resilience: 73, rainfall: 55, temperature: 25 },
    { month: "Sep", resilience: 76, rainfall: 70, temperature: 27 },
    { month: "Oct", resilience: 79, rainfall: 85, temperature: 29 },
    { month: "Nov", resilience: 81, rainfall: 110, temperature: 30 },
    { month: "Dec", resilience: score, rainfall: 95, temperature: 28 },
  ]

  // Mock factor breakdown data
  const factorData = [
    { name: "Soil Health", value: 25, color: "#4caf50" },
    { name: "Water Availability", value: 30, color: "#2196f3" },
    { name: "Weather Patterns", value: 20, color: "#ff9800" },
    { name: "Crop Variety", value: 15, color: "#9c27b0" },
    { name: "Management Practices", value: 10, color: "#607d8b" },
  ]

  // Mock monthly weather patterns
  const weatherData = [
    { month: "Jan", rainfall: 45, temperature: 28, humidity: 65 },
    { month: "Feb", rainfall: 38, temperature: 30, humidity: 62 },
    { month: "Mar", rainfall: 42, temperature: 32, humidity: 68 },
    { month: "Apr", rainfall: 85, temperature: 29, humidity: 75 },
    { month: "May", rainfall: 120, temperature: 27, humidity: 80 },
    { month: "Jun", rainfall: 95, temperature: 25, humidity: 78 },
    { month: "Jul", rainfall: 65, temperature: 24, humidity: 72 },
    { month: "Aug", rainfall: 55, temperature: 25, humidity: 70 },
    { month: "Sep", rainfall: 70, temperature: 27, humidity: 73 },
    { month: "Oct", rainfall: 85, temperature: 29, humidity: 76 },
    { month: "Nov", rainfall: 110, temperature: 30, humidity: 78 },
    { month: "Dec", rainfall: 95, temperature: 28, humidity: 74 },
  ]

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-lg max-w-xs">
          <p className="font-medium text-foreground text-sm sm:text-base">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-xs sm:text-sm mt-1" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
              {entry.name === "Temperature"
                ? "°C"
                : entry.name === "Rainfall"
                  ? "mm"
                  : entry.name === "Humidity"
                    ? "%"
                    : "%"}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  const CustomPieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-lg max-w-xs">
          <p className="font-medium text-foreground text-sm sm:text-base">{payload[0].name}</p>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">{payload[0].value}% contribution</p>
        </div>
      )
    }
    return null
  }

  return (
    <Card className="animate-fade-in">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
          <BarChart3 className="h-5 w-5 text-primary flex-shrink-0" />
          <span className="text-balance">Data Analytics for {county}</span>
        </CardTitle>
        <p className="text-sm text-muted-foreground">Detailed insights and historical trends</p>
      </CardHeader>
      <CardContent className="px-3 sm:px-6">
        <Tabs defaultValue="trends" className="w-full">
          <TabsList className="grid w-full grid-cols-3 h-12 sm:h-10 mb-6">
            <TabsTrigger
              value="trends"
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 min-h-[44px] text-xs sm:text-sm"
            >
              <TrendingUp className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline sm:inline">Trends</span>
            </TabsTrigger>
            <TabsTrigger
              value="factors"
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 min-h-[44px] text-xs sm:text-sm"
            >
              <PieChartIcon className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline sm:inline">Factors</span>
            </TabsTrigger>
            <TabsTrigger
              value="weather"
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 min-h-[44px] text-xs sm:text-sm"
            >
              <Calendar className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline sm:inline">Weather</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="trends" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Historical Resilience Trends
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  12-month resilience score progression with rainfall correlation
                </p>
              </div>
              <div className="h-64 sm:h-80 w-full overflow-hidden">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={historicalData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                      dataKey="month"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={10}
                      tick={{ fontSize: 10 }}
                      interval={0}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={10} tick={{ fontSize: 10 }} width={40} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontSize: "12px" }} iconSize={12} />
                    <Line
                      type="monotone"
                      dataKey="resilience"
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                      dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 3 }}
                      activeDot={{ r: 5, stroke: "hsl(var(--primary))", strokeWidth: 2 }}
                      name="Resilience Score"
                    />
                    <Line
                      type="monotone"
                      dataKey="rainfall"
                      stroke="hsl(var(--chart-2))"
                      strokeWidth={2}
                      dot={{ fill: "hsl(var(--chart-2))", strokeWidth: 2, r: 2 }}
                      name="Rainfall (mm)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="factors" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Resilience Factor Breakdown
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Contributing factors to your current resilience score
                </p>
              </div>
              <div className="h-64 sm:h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={factorData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {factorData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomPieTooltip />} />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }}
                      formatter={(value, entry) => <span style={{ color: entry.color }}>{value}</span>}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-1 gap-3 mt-4 px-1">
                {factorData.map((factor, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg min-h-[60px] touch-manipulation"
                  >
                    <div className="w-4 h-4 rounded-full flex-shrink-0" style={{ backgroundColor: factor.color }} />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm text-foreground truncate">{factor.name}</p>
                      <p className="text-xs text-muted-foreground">{factor.value}% contribution</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="weather" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Monthly Weather Patterns
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Rainfall, temperature, and humidity trends throughout the year
                </p>
              </div>
              <div className="h-64 sm:h-80 w-full overflow-hidden">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weatherData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                      dataKey="month"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={10}
                      tick={{ fontSize: 10 }}
                      interval={0}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={10} tick={{ fontSize: 10 }} width={40} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontSize: "12px" }} iconSize={12} />
                    <Bar dataKey="rainfall" fill="hsl(var(--chart-2))" name="Rainfall (mm)" radius={[2, 2, 0, 0]} />
                    <Bar
                      dataKey="temperature"
                      fill="hsl(var(--secondary))"
                      name="Temperature (°C)"
                      radius={[2, 2, 0, 0]}
                    />
                    <Bar dataKey="humidity" fill="hsl(var(--chart-3))" name="Humidity (%)" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
