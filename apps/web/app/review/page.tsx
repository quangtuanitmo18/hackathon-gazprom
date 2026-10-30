import { redirect } from "next/navigation";
import { auth, signOut } from "@/auth";
import { ReviewConsole } from "@/components/review-console";
export const dynamic="force-dynamic";

export default async function ReviewPage(){
  if(process.env.PRODUCTPULSE_AUTH_MODE!=="oidc"){
    return <section className="content-stack"><div className="eyebrow">INDEPENDENT REVIEW / DISABLED</div>
      <h1>Экспертная проверка недоступна</h1>
      <p className="lead">Для записи независимых решений необходимы личные аккаунты Keycloak. Общий пароль демо недостаточен.</p>
    </section>;
  }
  const session=await auth();
  if(!session?.user)redirect("/login");
  return <section className="content-stack">
    <div className="eyebrow">HUMAN REVIEW / SOURCE-SCOPED EVIDENCE</div>
    <div className="section-heading"><h1>Независимая проверка инцидентов</h1><form action={async()=>{"use server";await signOut({redirectTo:"/login"});}}><button className="review-refresh" type="submit">Выйти из ProductPulse</button></form></div>
    <p className="lead">Выберите два обращения, изучите их независимо и укажите, относятся ли они к одной технической причине. Сходный текст сам по себе не является доказательством.</p>
    <ReviewConsole displayName={session.user.name||"Эксперт"}/>
  </section>;
}
