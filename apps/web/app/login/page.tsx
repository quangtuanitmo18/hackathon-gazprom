import { signIn } from "@/auth";
import { KeyRound, ShieldCheck } from "lucide-react";
export const dynamic="force-dynamic";

export default function LoginPage(){
  if(process.env.PRODUCTPULSE_AUTH_MODE!=="oidc"){
    return <section className="content-stack"><h1>Вход через OIDC недоступен</h1><p>Включите Keycloak, чтобы открыть независимую экспертную проверку.</p></section>;
  }
  return <section className="content-stack">
    <div className="eyebrow">INDEPENDENT HUMAN REVIEW</div>
    <h1>Вход эксперта</h1>
    <p className="lead">Для подтверждения независимых решений требуется индивидуальная учётная запись Keycloak. Общий пароль демо не допускается.</p>
    <form action={async()=>{"use server";await signIn("keycloak",{redirectTo:"/review"});}}>
      <button type="submit" className="login-button"><KeyRound size={18}/> Войти через Keycloak</button>
    </form>
    <div className="explanation"><ShieldCheck size={17}/><p>Доступ к тикетам и экспертным оценкам предоставляется только после проверки токена OIDC на сервере.</p></div>
  </section>;
}
