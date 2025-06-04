import RadioAppFullscreen from "@/components/radio-app-fullscreen"

export default function HomePage() {
  return (
    <div className="h-screen w-screen overflow-hidden bg-gradient-to-br from-slate-950 via-purple-950 to-black text-slate-200 selection:bg-purple-500 selection:text-white">
      <RadioAppFullscreen />
    </div>
  )
}
