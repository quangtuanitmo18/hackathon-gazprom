import type { Metadata } from "next";
import Link from "next/link";
import { Activity, ArrowUpRight, ClipboardList, Layers3, Lightbulb, ShieldCheck, UsersRound } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "ProductPulse AI | Incident Intelligence",
  description: "Evidence-first support incident intelligence dashboard",
  robots: { index: false, follow: false },
};

const nav = [
  { href: "/", label: "Проблемы", icon: Layers3 },
  { href: "/audit", label: "Аудит", icon: ClipboardList },
  ...(process.env.PRODUCTPULSE_AUTH_MODE==="oidc" ? [
    {href:"/review",label:"Экспертная проверка",icon:UsersRound},
    {href:"/insights",label:"Предложения",icon:Lightbulb},
  ] : []),
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>
        <div className="app-shell">
          <aside className="sidebar">
            <Link href="/" className="brand" aria-label="ProductPulse AI">
              <span className="brand-icon"><Activity size={21} strokeWidth={2.8} /></span>
              <span><strong>ProductPulse</strong><small>INTELLIGENCE ENGINE</small></span>
            </Link>
            <div className="sidebar-label">РАБОЧАЯ ОБЛАСТЬ</div>
            <nav className="navigation" aria-label="Главная навигация">
              {nav.map(({href,label,icon: Icon}) => (
                <Link key={href} href={href} className="nav-link">
                  <Icon size={17} strokeWidth={1.9}/>{label}<ArrowUpRight size={14} className="nav-arrow"/>
                </Link>
              ))}
            </nav>
            <div className="sidebar-bottom">
              <div className="secure-label"><ShieldCheck size={16}/> {process.env.PRODUCTPULSE_AUTH_MODE === "oidc" ? "Персональный вход Keycloak" : "Закрытый демо-доступ"}</div>
              <small>Инциденты подтверждаются людьми. Совпадение текстов не доказывает общую причину.</small>
            </div>
          </aside>
          <div className="workspace">
            <header className="topbar">
              <div className="topbar-crumb"><span className="topbar-dot"/>Support Intelligence <span className="crumb-separator">/</span> Рабочая панель</div>
              <span className="topbar-environment"><span className="pulse-dot"/> DEMO ENVIRONMENT</span>
            </header>
            <main className="main-content">{children}</main>
            <footer className="footer">ProductPulse AI · Source-scoped evidence · Данные без искусственно завышенных метрик</footer>
          </div>
        </div>
      </body>
    </html>
  );
}
