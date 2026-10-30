import {redirect} from "next/navigation";
import {auth} from "@/auth";
import {InsightConsole} from "@/components/insight-console";

export const dynamic="force-dynamic";

export default async function InsightPage(){
  if(process.env.PRODUCTPULSE_AUTH_MODE!=="oidc")
    return <section className="content-stack">
      <div className="eyebrow">INSIGHT PROPOSALS / DISABLED</div>
      <h1>Предложения недоступны</h1>
      <p className="lead">Для ручного подтверждения нужен личный вход Keycloak. Общий демо-пароль не даёт право публикации.</p>
    </section>;
  const session=await auth();
  if(!session?.user)redirect("/login");
  return <section className="content-stack">
    <div className="eyebrow">HUMAN-GATED / VERIFIED PROBLEM MEMBERSHIP</div>
    <h1>Предложения продуктовой команде</h1>
    <p className="lead">
      Только явно объединённые после независимой проверки проблемы. Ни общий root cause, ни бизнес-эффект системой не доказаны.
      Все варианты требуют решения человека; публикация возможна только в учебный mock tracker.
    </p>
    <InsightConsole displayName={session.user.name||"Эксперт"}/>
  </section>;
}
