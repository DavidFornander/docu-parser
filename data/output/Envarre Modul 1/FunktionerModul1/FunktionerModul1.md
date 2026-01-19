<!-- image -->

Institutionen f¨ or Matematik

SF1626

Flervariabelanalys

L¨ as ˚

aret 2024-25

Tommy Ekola, Lars Filipsson, Roy Skjelnes

## Modul I Funktioner

## Modul I

I bokens kapitel 10 ¨ ar avsnitt 10.6 fr¨ amst i fokus med cylindriska och sf¨ ariska koordinater. ¨ Aven avsnitt 10.1 ¨ ar viktigt. D¨ ar inf¨ ors de topologiska begreppen: omgivning, inre och yttre punkter, randpunkter, ¨ oppen m¨ angd och sluten m¨ angd.

Kapitel 12: Kontinuerliga vektorv¨ arda funktioner av en reell variabel kan ses som parametriseringar av kurvor. Tv˚ a vanliga tolkningar finns. Antingen ¨ ar man intresserad av sj¨ alva kurvan, hur den ser ut, vad den har f¨ or tangenter i olika punkter, vad den har f¨ or l¨ angd. Eller s˚ a t¨ anker man sig att en partikel r¨ or sig l¨ angs kurvan, vad den har f¨ or hastighet, fart och acceleration, hur l˚ angt den f¨ ardas. Om en vektorv¨ ard funktion av en reell variabel ¨ ar deriverbar s˚ a ¨ ar dess derivata en vektor, som ¨ ar en tangentvektor till kurvan och som beskriver hastigheten i fall vi har en partikel som r¨ or sig. L¨ angden av denna vektor ¨ ar i s˚ a fall farten och det ¨ ar integralen av den som ¨ ar l¨ angden av kurvan. Andraderivatan ¨ ar ocks˚ a en vektor, som beskriver accelerationen i fall vi har en partikel som r¨ or sig.

I kapitel 13 b¨ orjar studiet av reellv¨ arda funktioner av flera variabler, med definitionsm¨ angd, v¨ ardem¨ angd, graf. Gr¨ ansv¨ arde och kontinuitet ¨ ar grundl¨ aggande begrepp som det ¨ ar viktigt att f¨ orst˚ a nu. Senare, i n¨ asta modul, ska vi derivera ocks˚ a. Missa inte begreppen niv˚ akurva och niv˚ ayta, som fungerar ungef¨ ar som h¨ ojdkurvor p˚ a topografiska kartor. De kommer att vara anv¨ andbara.

Inramningen f¨ or modulen ¨ ar 6 timmar f¨ orel¨ asningar, 4 timmar workshop, samt 2 timmar seminarium.

## Koordinatsystem

- F¨ orst ˚ a och anv¨ anda pol¨ ara koordinater f¨ or att beskriva m¨ angder i R 2 .
- F¨ orst ˚ a och anv¨ anda cylindriska koordinater f¨ or att beskriva m¨ angder i R 3 .
- F¨ orst ˚ a och anv¨ anda sf¨ ariska koordinater f¨ or att beskriva m¨ angder i R 3 .

## 1.1 Pol¨ ara koordinater

I planet anv¨ ander vi ofta pol¨ ara koordinater . En noll-skilld vektor i R 2 kan beskrivas med avst˚ andet fr˚ an origo, och vinkeln - som vi m¨ ater moturs fr˚ an x -axeln. Om ( x, y ) ¨ ar koordinaterna till en noll-skilld vektor har vi relationerna

<!-- formula-not-decoded -->

d¨ ar r = √ x 2 + y 2 , och med vinkeln 0 ≤ θ &lt; 2 π .

Exempel 1. Olikheterna 1 ≤ x 2 + y 2 ≤ 4 best¨ ammer ett omr˚ ade, en s˚ akallad annulus, A i planet. I pol¨ ara koordinater ¨ ar A det rektangul¨ ara omr˚ adet d¨ ar 1 ≤ r ≤ 2 och 0 ≤ θ &lt; 2 π .

## 1.2 Cylinderkoordinater

F¨ or 3-rummet R 3 anv¨ ander vi ofta en av tv˚ a koordinatbyten. Den ena ¨ ar en naturlig utvigning av pol¨ ara koordinater. Vi l¨ agger simpelthen till tredje koordinaten. Det vill s¨ aga om ( x, y, z ) ¨ ar koordinaterna till en punkt i R 3 , d ˚ a ges denna punkt med cylinderkoordinater ( r, θ, z ) vilka best¨ ams av relationerna

<!-- formula-not-decoded -->

d¨ ar r = √ x 2 + y 2 , och med vinkeln 0 ≤ θ &lt; 2 π . Punkterna p˚ a formen (0 , 0 , z ) ¨ ar vad vi kallar z -axeln, ¨ ar inte beskrivna med cylinderkoordinater.

## 1.3 Sf¨ ariska koordinater

De sf¨ ariska koordinaterna ( R,ϕ,θ ) ¨ ar lite sv˚ arare att visualisera vid f¨ orsta m¨ ote, men ¨ ar end˚ a mycket naturliga. En given punkt ( x, y, z ) befinner sig p˚ a en unik sf¨ ar centrerad omkring origo. Radien av denna sf¨ ar ¨ ar R = √ x 2 + y 2 + z 2 . Vi l˚ ater positiva z -axeln best¨ amma nordpolen p˚ a varje s˚ adan sf¨ ar. P˚ a sf¨ aren som inneh˚ aller punkten ( x, y, z ) har vi att punkten ligger p˚ a en unik breddgrad. Vinkeln fr˚ an nordpolen tilll denna breddgrad blir n˚ agot v¨ arde 0 ≤ ϕ ≤ π . (M¨ ark att vinkeln inte kan ¨ overstiga π ). Slutligen beh¨ over vi specifiera vilken merdian som punkten befinner sig p˚ a. Merdianen anges med en vinkel 0 ≤ θ &lt; 2 π som vi m¨ ater moturs (med z pekande upp˚ at) fr˚ an positiva x -axeln. Relationerna mellan en punkt med koordinater( x, y, z ) och sf¨ ariska koordinater ( R,ϕ,θ ) ¨ ar

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## Uppgifter

Uppgift 1.1. Beskriv nedanst˚ aende omr˚ aden i pol¨ ara koordinater. (En ruta = en l¨ angdenhet.)

<!-- image -->

Uppgift 1.2. Skissera f¨ oljande omr˚ aden uttryckta i pol¨ ara koordinater.

- a) r ≤ 4
- b) π/ 4 ≤ θ ≤ 3 π/ 4
- c) 0 ≤ r ≤ 5 , π ≤ θ ≤ 3 π/ 2
- d) r = 2 , 0 ≤ θ ≤ π
- e) 1 ≤ r ≤ 3 , θ = π/ 4
- f) r = 0

Uppgift 1.3. Beskriv nedanst˚ aende omr˚ aden dels i rektangul¨ ara koordinater, dels i pol¨ ara koordinater.

<!-- image -->

Uppgift 1.4. Hur beskrivs Ω = { ( x, y ) : 1 ≤ x 2 + y 2 ≤ 3 och | x | &lt; y } i pol¨ ara koordinater.

Uppgift 1.5. Beskriv omr˚ adet i cylindriska koordinater. (En ruta = en l¨ angdenhet.)

<!-- image -->

4

Uppgift 1.6. Rita upp f¨ oljande omr˚ aden beskrivna i cylindriska koordinater f¨ orst i ( r, z )-planet och d¨ arefter i xyz -rymden.

- a) 0 ≤ r ≤ 3, 0 ≤ z ≤ 4
- b) z = 2 r , z ≤ 4
- c) 0 ≤ z ≤ 5 -r 2 / 3

Uppgift 1.7. Skissera f¨ oljande omr˚ aden beskrivna i sf¨ ariska koordinater.

- a) 0 ≤ r ≤ 5, 0 ≤ ϕ ≤ π/ 6, π/ 2 ≤ θ ≤ 2 π
- b) 0 ≤ r ≤ 5, π/ 18 ≤ ϕ ≤ π/ 4, 0 ≤ θ ≤ π/ 2

Uppgift 1.8. Beskriv f¨ oljande fj¨ ardedelsklot med radie a dels i rektangul¨ ara koordinater, dels i rymdpol¨ ara koordinater.

<!-- image -->

Uppgift 1.9. Hur beskrivs m¨ angden K = { ( x, y, z ) : x 2 + y 2 + z 2 &lt; 9 , y &gt; 0 och z &gt; 0 } i sf¨ ariska koordinater?

## Topologi

- F¨ orst ˚ a och anv¨ anda begreppet omgivning.
- Identifiera inre punkter, yttre punkter och randpunkter till en m¨ angd.
- Avg¨ ora om en m¨ angd ¨ ar ¨ oppen, sluten eller ingetdera.

## 2.1 ¨ Oppna och slutna m¨ angder

Av rent notationstekniska sk¨ al introduceras topologiska begrepp f¨ or planet R 2 . Generaliseringarna till godtyckliga R n l¨ amnas till l¨ asaren.

## ¨ Oppen boll

L˚ at P = ( a, b ) vara en punkt i planet. Till varje ϵ &gt; 0 har vi cirkeln centrerad omkring ( a, b ) med radie ϵ . Insidan av cirkeln ¨ ar definierad som

<!-- formula-not-decoded -->

M¨ angden B ϵ ( P ) kallas den ¨ oppna skivan, eller den ¨ oppna bollen , omkring P med radie ϵ .

## ¨ Oppna omgivningar

L˚ at U vara en delm¨ angd i R 2 . En punkt P ∈ U ligger i det indre av m¨ angden U om det existerar en ¨ oppen boll B ϵ ( P ) inkluderad i U . M¨ angden U ¨ ar ¨ oppen om U ¨ ar lika med dess indre, vilket betyder att varje punkt i U ocks˚ a finns i det indre av U . En ¨ oppen omgivning omkring en punkt P betyder en ¨ oppen, ospecifierad, m¨ angd som inneh˚ aller punkten P .

## Slutna m¨ angder

En delm¨ angd C i R 2 ¨ ar sluten om komplementet till C ¨ ar en ¨ oppen m¨ angd. En punkt P i R 2 ¨ ar en randpunkt till en m¨ angd C om varje ¨ oppen boll omkring P inneh˚ aller punkt fr˚ an C och fr˚ an komplementet till C . En m¨ angd C ¨ ar sluten om den inneh˚ aller dess randpunkter ∂C . En sluten m¨ angd C ¨ ar den disjunkta unionen av dess indre och dess rand.

## Kompakta m¨ angder

En m¨ angd C i R 2 ¨ ar begr¨ ansad om m¨ angden C ¨ ar inneh˚ allen i n˚ agon l˚ ada { ( x 1 , x 2 ) | | x i | ≤ N,i = 1 , 2 } , d¨ ar N ¨ ar en konstant. En m¨ angd C i R 2 som ¨ ar sluten och begr¨ ansad ¨ ar en kompakt m¨ angd.

## Uppgifter

## Uppgift 2.10.

- a) Visa att m¨ angden C 1 = { ( x, y ) | x 2 = y } ¨ ar en sluten, men ej en kompakt m¨ angd.
- b) Visa att m¨ angden C 2 = { ( x, y ) | x 2 = y, y ≤ 5 } ¨ ar kompakt.
- c) Visa att m¨ angden C 3 = { ( x, y ) | x 2 = y, y &lt; 5 } ej ¨ ar kompakt.

̸

- d) Best¨ am randpunkterna till C 4 = { ( x, y ) | x 2 = y, x = 0 } .

## Uppgift 2.11. Hitta exempel som satisfierar f¨ oljande.

- a) En m¨ angd som varken ¨ ar sluten eller ¨ oppen.
- b) En m¨ angd som ¨ ar sluten och ¨ oppen.

## Kurvor

- Hantera vektorv¨ arda funktioner av en reell variabel.
- Tolka s˚ adana funktioner i termer av kurvor och partikelr¨ orelse.
- Definiera, ber¨ akna och tolka derivator av vektorv¨ arda funktioner.
- Ta fram tangentvektorer och tangentlinjer.
- Ber¨ akna hastighet, fart och acceleration av partikel som r¨ or sig.
- R¨ akna ut b˚ agl¨ angd av en parameterkurva.

## 3.1 Vektorv¨ arda funktioner

En funktion r : R → R n tillordnar till varje reelt tal t ∈ R en vektor r ( t ) i R n , det vill s¨ aga ett ordnat n -tuppel r ( t ) = ( x 1 ( t ) , . . . , x n ( t )) av reella tal. Liknande har vi en att en funktion r : [ a, b ] -→ R n tillordnar en vektor r ( t ) f¨ or varje tal i intervallet a ≤ t ≤ b . S˚ adana funktioner kallas vektorv¨ arda funktioner.

## Koordinatfunktioner

Att specifiera en vektorv¨ ard funktion r : R → R n ¨ ar att specifiera en ordnad sekvens x 1 , x 2 , . . . , x n av reellv¨ arda funktioner x i : R → R (med i = 1 , . . . , n ). Funktionerna x 1 , x 2 , . . . , x n kallar vi koordinatfunktionerna till r .

## Derivator

Om koordinatfunktionerna till en vektorv¨ ard funktion r : R -→ R n ¨ ar deriverbara f˚ ar vi en ny vektorv¨ ard funktion d r : R → R n definerad av uttrycket

<!-- formula-not-decoded -->

Anm¨ arkning 3.1.1 . Vi kan f¨ orest¨ alla oss att r ( t ) ¨ ar en funktion som sveper ut positionen till en partikel vid tiden t . Om dess koordinatfunktioner ¨ ar deriverbara d˚ a beskriver d r hastigheten till partikeln vid positionen r ( t ). Om nu koordinatfunktionerna till d r ¨ ar deriverbara d˚ a ¨ ar accelerationen, som f˚ as via derivering av koordinatfunktionerna till d r , ocks˚ a en vektorv¨ ard funktion.

## 3.2 Kurvor och parametrisering

## Kurvor

L˚ at r : [ a, b ] -→ R n vara en vektorv¨ ard funktion d¨ ar koordinatfunktionerna x 1 , . . . , x n ¨ ar deriverbara. Bildm¨ angden C ¨ ar m¨ angden av vektorer r ( t ) med a ≤ t ≤ b , och kallas en kurva i R n .

Exempel 2. L¨ osningsm¨ angden till ekvationen x 2 + y 2 = 1 blir enhetscirkeln. Denna kurva kan vi beskriva som bilden av funktionen r ( t ) = (cos( t ) , sin( t )) med 0 ≤ t ≤ 2 π .

Bilden av funktionen r ( t ) = ( t 2 , t 3 ), med godtyckliga t , ger en kurva i planet som kan beskrivas av ekvationen y 3 = x 2 .

I rummet, R 3 vill inte en kurva vara givet av en ekvation. Ett exempel ¨ ar x -axeln i rummet. Detta ¨ ar en linje, och ¨ ar en kurva som vi kan beskriva med funktionen r ( t ) = ( t, 0 , 0), med godtyckliga t .

## Sl¨ at kurva

L˚ at r : [ a, b ] → R n vara en funktion med deriverbara koordinatfunktioner. Bilden till funktionen r ¨ ar d¨ armed en kurva C . Om derivatan d r ( t ) ger en noll-skilld riktningsvektor f¨ or tangentlinjen till kurvan C i varje punkt r ( t ) d˚ a s¨ ager vi att kurvan C ¨ ar sl¨ at. Tangentlinjen till en sl¨ at kurva i punkten r ( c ) ges d¨ armed av uttrycket

<!-- formula-not-decoded -->

med godtyckliga t .

Exempel 3. Kurvan som best¨ ams av funktionen r ( t ) = ( t 2 , t 3 ) ¨ ar inte sl¨ at i punkten r (0) = (0 , 0) d˚ a derivatan av komponentfunktionerna ¨ ar noll i denna punkt.

## Orientering

L˚ at r : [ a, b ] -→ R n vara en vektorv¨ ard funktion vars bild ¨ ar en kurva C . Kurvan b¨ orjar i punkten r ( a ) och slutar i r ( b ). Riktningen som vi traverserar punkterna till kurvan C kallar vi f¨ or orienteringen till kurvan. Om r ( a ) = r ( b ) d˚ a b¨ orjar och slutar kurvan i samma punkt, och en s˚ adan kurva ¨ ar en sluten kurva.

## Parametriserad kurva

L˚ at C vara en kurva, och l˚ at r : [ a, b ] -→ R n vara en vektorv¨ ard funktion vars bild ¨ ar kurvan C . Om funktionen r ¨ ar injektiv, fr˚ ans¨ att ett ¨ andligt antal tal i intervallet [ a, b ], d˚ a ¨ ar funktionen r en parametrisering av kurvan C .

Exempel 4. Bilden av funktionen r ( t ) = (cos( t ) , sin( t )) d¨ ar 0 ≤ t ≤ 2 π ¨ ar enhetscirkeln C i planet. Funktionen r ¨ ar inte injektiv d˚ a ¨ andpunkterna r (0) = r (2 π ) ¨ ar identifierade. Borts¨ att from dessa tal ¨ ar funktionen injektiv, och f¨ oljdaktligen ¨ ar funktionen en parametrisering av cirkeln.

Om vi ist¨ allet l ˚ ater 0 ≤ t ≤ 4 π d˚ a ¨ andras inte bilden till funktionen r ( t ) = (cos( t ) , sin( t )). Bilden ¨ ar fortfarande enhetscirkeln C . Nu genoml¨ oper vi cirkeln tv˚ a g˚ anger, och funktionen ¨ ar inte en parametrisering av cirkeln.

## Exempel 5. Ekvationssystemet

<!-- formula-not-decoded -->

i tre ok¨ anda ( x, y, z ) ¨ ar en rymdkurva C . Notera att den f¨ orsta ekvationen beskriver en cirkel med radie 2 i ( x, y )-planet, men att z -v¨ ardet ¨ ar godtyckligt. L¨ osningen till denna ekvation ¨ ar en cylinder. Sk¨ arningen av denna cylinder med planet { z = x + 2 y } ¨ ar rymdkurvan C . En parametrisering av denna kurva ¨ ar

<!-- formula-not-decoded -->

## 3.3 B˚ agl¨ angd

L˚ at r : [ a, b ] -→ R n vara en parametrisering av en sl¨ at kurva C . Till varje a ≤ t ≤ b har vi hastighetsvektorn d r ( t ) = (˙ x 1 ( t ) , · · · , ˙ x n ( t )). L¨ angden av hastighetsvektorn d r ( t ) ¨ ar

<!-- formula-not-decoded -->

Vi definerar b ˚ agl¨ angden till kurvan C som

<!-- formula-not-decoded -->

Anm¨ arkning 3.3.1 . Definitionen av b˚ agl¨ angd anv¨ ander en parametrisering av kurvan, men det visar sig att b˚ agl¨ angden ¨ ar oberoende av val av parametrisering.

Exempel 6. Funktionen r ( t ) = (2cos( t ) , 2 sin( t ) , 5 t ) beskriver en cirkul¨ ar helixkurva C . N¨ ar 0 ≤ t ≤ 4 π vill kurvan b¨ orja i punkten (2 , 0 , 0) och d¨ arefter ˚ ama sig runt cylindern x 2 + y 2 = 4 tv˚ a g˚ anger med slutpunkt (2 , 0 , 20 π ). F¨ or att best¨ amma b˚ agl¨ angden anv¨ ander vi uttryck f¨ or hastigheten, som ¨ ar d r ( t ) = ( -2 sin( t ) , 2 cos( t ) , 5). Definitionen av b˚ agl¨ angden ger nu att

<!-- formula-not-decoded -->

## 3.4 Linjeintegral

Antag nu att vi har en funktion f : C -→ R d¨ ar C ¨ ar en sl¨ at kurva. Om r ( t ) ¨ ar en parametrisering av kurvan C d˚ a har vi att sammans¨ attningen f ( r ( t )) ¨ ar en funktion i en variabel t , med a ≤ t ≤ b . Om funktionen f ( r ( t )) ¨ ar kontinuerlig defineras linjeintegralen enligt

<!-- formula-not-decoded -->

Exempel 7. L˚ at C vara delen av parabolan y = x 2 d¨ ar 0 ≤ x ≤ 2. T¨ athetsfunktionen f : C -→ R tillordnar talet f ( x, y ) = x till en punkt ( x, y ) p˚ a kurvan C . Med denna t¨ athetsfunktion blir vikten av kurvan lika med linjeintegralen ∫ C fds . Vi vill best¨ amma denna vikt. En parametrisering

av kurvan ¨ ar r ( t ) = ( t, t 2 ) d¨ ar 0 ≤ t ≤ 2. Vi har att d r ( t ) = (1 , 2 t ), och d¨ armed att | d r ( t ) | = √ 1 + 4 t 2 . Kurvans vikt ges av uttrycket

<!-- formula-not-decoded -->

Funktionen φ ( t ) = 1 12 (1+4 t 2 ) 3 / 2 ¨ ar en primitiv funktion till t √ 1 + 4 t 2 . Detta ger att ∫ C fds = [ φ ( t )] 2 0 = 1 12 (27 -1) = 13 2 .

## Uppgifter

Uppgift 3.12. Parametrisera kurvan

<!-- formula-not-decoded -->

Uppgift 3.13. Parametrisera nedanst˚ aende kurvor:

- a) Cirkeln 2 x 2 +4 x +2 y 2 = 6.
- b) Linjestycket y = 3 x +5, d˚ a 0 ≤ x ≤ 3.
- c) Ellipsen x 2 +4 y 2 = 4.

Uppgift 3.14. En partikel r¨ or sig l¨ angs en kurva i R 2 s˚ a att den vid tidpunkten t sekunder efter starten befinner sig i punkten r ( t ) = (2cos πt, sin πt ). Enheten p˚ a axlarna ¨ ar meter.

- a) Vilken typ av kurva r¨ or sig partikeln l¨ angs?
- b) Best¨ am partikelns hastighet, fart och acceleration vid tidpunkten t = 2.

Uppgift 3.15. En partikel r¨ or sig i planet l¨ angs en ellipskurva s˚ a att den vid tidpunkten t ≥ 0 befinner sig i punkten

<!-- formula-not-decoded -->

- a) I vilka punkter p˚ a kurvan ¨ ar farten som st¨ orst?

- b) Best¨ am den st¨ orsta farten.

Uppgift 3.16. En partikel r¨ or sig l¨ angs en kurva i R 3 s˚ a att den vid tidpunkten t sekunder efter starten befinner sig i punkten r ( t ) = ( t, t 2 , t 3 ). Enheten p˚ a axlarna ¨ ar meter. Best¨ am partikelns hastighet, fart och acceleration i tidpunkten t = 1.

Uppgift 3.17. En kurva i R 3 parametriseras genom r ( t ) = ( t, t 2 , 4) d¨ ar t ∈ R .

- a) Hur vet man att punkten (2 , 4 , 4) ligger p˚ a kurvan?
- b) Best¨ am en parameterframst¨ allning av tangentligen till kurvan i punkten (2 , 4 , 4).
- c) Skriv upp en integral som ger l¨ angden av den del av kurvan som ligger mellan punkten ( -2 , 4 , 4) och (2 , 4 , 4).

Uppgift 3.18. Betrakta spiralkurvan ( x, y, z ) = (cos 2 πt, sin 2 πt, t ) d¨ ar t ∈ R .

- a) Verifiera att punkten (1 , 0 , 1) ligger p˚ a kurvan.
- b) Best¨ am en tangentvektor till kurvan i punkten (1 , 0 , 1).
- c) Best¨ am en parametrisering av tangentlinjen till kurvan i punkten (1 , 0 , 1).
- d) Best¨ am l¨ angden av den del av spiralkurvan som f˚ as d˚ a 0 ≤ t ≤ 1.

## Tentamensuppgifter

Tentamen. 20.01.10, Problem 1B. Kurvan C parametriseras av r ( t ) = (3 cos(2 t ) , 1+cos 2 (2 t )) med -π/ 2 ≤ t ≤ 0. F¨ orklara varf¨ or f¨ oljande p˚ ast˚ aenden st¨ ammer.

- Punkterna ( x, y ) p˚ a kurvan satisfierar ekvationen y = 1 + x 2 / 9.
- Kurvan ¨ ar symmetrisk om y -axeln.

- Avst˚ andet fr˚ an kurvan till origo ¨ ar 1.
- B˚ agl¨ angden till kurvan ¨ ar 1 9 ∫ 3 -3 √ 81 + 4 t 2 dt .
- Kurvan ¨ ar sl¨ at.

## Funktioner i flera variabler

- Hantera reellv¨ arda funktioner av flera variabler.
- Resonera kring gr¨ ansv¨ arde och kontinuitet f¨ or s˚ adana funktioner.
- Ber¨ akna gr¨ ansv¨ arden alternativt visa att gr¨ ansv¨ arde saknas.
- Ta fram definitionsm¨ angd och v¨ ardem¨ angd, graf.
- Best¨ amma och anv¨ anda niv˚ akurvor och -ytor.

## 4.1 Funktioner i flera variabler

L˚ at U ⊆ R m vara en ¨ oppen delm¨ angd. En funktion f : U -→ R tillordnar till varje vektor ( x 1 , . . . , x m ) i U ett tal f ( x 1 , . . . , x m ). S˚ adana funktioner kallas funktioner i flera variabler , eller en funktion i m variabler. M¨ angden U ¨ ar definitionsomr ˚ adet till funktionen, och m¨ angden

```
{ y ∈ R | y = f ( x 1 , . . . , x m ) n˚ agon vektor ( x 1 , . . . , x m ) ∈ U }
```

¨ ar v¨ ardem¨ angden till funktionen . Grafen till en funktionen ¨ ar delm¨ angden i U × R som best˚ ar av alla ( m +1)-tupler p˚ a formen ( x 1 , . . . , x m , f ( x 1 , . . . , x m )).

## Niv˚ akurva

Niv˚ akurvan till en funktion f : R m -→ R definieras som delm¨ angden av R m som best˚ ar av alla m -tupler ( x 1 , . . . , x m ) s ˚ adana att f ( x 1 , . . . , x m ) = c .

Med andra ord har vi att niv˚ akurvan ¨ ar den inversa bilden f -1 ( c ) till ett givet tal c .

Niv˚ akurvan till en funktion f ( x, y ) in tv˚ a variabler ¨ ar definierad av en ekvation c = f ( x, y ), och f¨ oljdaktligen ¨ ar dessa ofta kurvor. Niv˚ akurvorna till funktioner f ( x, y, z ) i tre variabler ¨ ar ofta ytor.

Exempel 8. Vi har funktionen f ( x, y ) = x 2 + y 2 i tv˚ a variabler x och y . Definitionsm¨ angden ¨ ar talplanet R 2 , och v¨ ardem¨ angden ¨ ar alla positiva tal y ≥ 0. Vi har vidare att till varje tal c har vi niv˚ akurvan c = x 2 + y 2 . Med c &lt; 0 vill niv˚ akurvan vara den tomma m¨ angden. Med c = 0 vill niv˚ akurvan vara punkten (0 , 0). Med c &gt; 0 vill niv ˚ akurvan vara cirkeln centrerad omkring origo, med radie √ c .

Grafen till funktionen f ¨ ar delm¨ angden av R 2 × R = R 3 givet av ekvationen z = f ( x, y ) = x 2 + y 2 . Detta ¨ ar en paraboloid yta. Sk¨ arningen av paraboloiden med det horisontella planet z = c ger, efter projektion ned p˚ a ( x, y )-planet, niv˚ akurvan.

## 4.2 Gr¨ ans och kontinuerliga funktioner

Gr¨ ansenbegr¨ appet f¨ or funktioner i flera variabler ¨ ar mera komplicerat ¨ an vad som ¨ ar fallet f¨ or en-variabel funktioner. Den formella definitionen ¨ ar dock den samma.

## Gr¨ ansbegreppet

Anta att funktionen f ( x, y ) ¨ ar definierad i en ¨ oppen omgiving omkring en punkt ( a, b ). Vi definierar gr¨ ansen lim ( x,y ) → ( a,b ) f ( x, y ) = L om det till varje ϵ &gt; 0 existerar n˚ agot δ &gt; 0 s˚ adan att

<!-- formula-not-decoded -->

f¨ or alla 0 &lt; | ( x, y ) -( a, b ) | &lt; δ .

## Kontinuitet

Anta att funktionen f ( x, y ) ¨ ar definierad i en ¨ oppen omgivning omkring punkten ( a, b ). Funktionen ¨ ar kontinuerlig i ( a, b ) om lim ( x,y ) → ( a,b ) f ( x, y ) = f ( a, b ).

- Sats 1. L˚ at f : U -→ R vara en funktion. Funktionen ¨ ar kontinuerlig om och endast om inversa bilden f -1 ( I ) ¨ ar ¨ oppen f¨ or varje ¨ oppen m¨ angd I i R .

Sats 2. Element¨ ara funktioner (sammans¨ attningar och algebraiska uttryck av polynom, rationella funktioner, rotfunktioner, trigonometriska funktioner, exponential och logaritm-funktioner) ¨ ar kontinuerliga.

## Uppgifter

Uppgift 4.19. Best¨ am definitionsm¨ angderna till f¨ oljande funktioner fr˚ an R 2 till R .

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Uppgift 4.20. Betrakta funktionen f ( x, y ) = x 2 + y 2 -1.

- a) Best¨ am definitionsm¨ angd och v¨ ardem¨ angd till f .
- b) Skissa n˚ agra niv˚ akurvor till f .
- c) Skissa grafen till f .

Uppgift 4.21. Skissa n˚ agra niv˚ akurvor/niv˚ aytor till nedanst˚ aende funktioner.

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Uppgift 4.22. Ber¨ akna nedanst˚ aende gr¨ ansv¨ arden eller bevisa att de inte existerar!

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Uppgift 4.23. I vilka punkter ¨ ar nedanst˚ aende funktioner kontinuerliga?

̸

<!-- formula-not-decoded -->

̸

<!-- formula-not-decoded -->

Uppgift 4.24. I vilka punkter ¨ ar nedanst˚ aende funktioner kontinuerliga?

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## Facit och l¨ osningstips

1.1.

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## 1.2.

<!-- image -->

- 1.3. a) Rektangul¨ ara koordinater: x 2 + y 2 ≤ 9, x -y ≥ 3 Pol¨ ara koordinater: 3 π/ 2 ≤ θ ≤ 2 π , 3 cos θ -sin θ ≤ r ≤ 3
- b) Rektangul¨ ara koordinater: x 2 +( y -2) 2 ≤ 4 Pol¨ ara koordinater: 0 ≤ θ ≤ π , 0 ≤ r ≤ 4 sin θ
- 1.4. 1 ≤ r ≤ √ 3 , π/ 4 &lt; θ &lt; 3 π/ 4.

## 1.5.

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## 1.6. I ( r, z )-planet:

<!-- image -->

<!-- image -->

c)

<!-- image -->

## I xyz -rymden:

<!-- image -->

- 1.8. a) Rektangul¨ ara koordinater: x 2 + y 2 + z 2 ≤ a 2 , y ≤ 0, z ≥ 0 Rymdpol¨ ara koordinater: 0 ≤ r ≤ a , 0 ≤ ϕ ≤ π/ 2, π ≤ θ ≤ 2 π
- b) Rektangul¨ ara koordinater: x 2 + y 2 + z 2 ≤ a 2 , x ≤ 0, z ≥ 0 Rymdpol¨ ara koordinater: 0 ≤ r ≤ a , 0 ≤ ϕ ≤ π/ 2, π/ 2 ≤ θ ≤ 3 π/ 2
- c) Rektangul¨ ara koordinater: x 2 + y 2 + z 2 ≤ a 2 , x ≤ 0, y ≥ 0 Rymdpol¨ ara koordinater: 0 ≤ r ≤ a , 0 ≤ ϕ ≤ π , π/ 2 ≤ θ ≤ π
- d) Rektangul¨ ara koordinater: x 2 + y 2 + z 2 ≤ a 2 , y ≥ 0, z ≤ 0 Rymdpol¨ ara koordinater: 0 ≤ r ≤ a , π/ 2 ≤ ϕ ≤ π , 0 ≤ θ ≤ π
- 1.9. 0 &lt; r &lt; 3 , 0 &lt; ϕ &lt; π/ 2 , 0 &lt; θ &lt; π

## 2.10.

- a) L˚ at P = ( a, b ) vara en punkt ej med i m¨ angden C 1 . V¨ alj ϵ att vara ett positivt tal som ¨ ar mindre ¨ an avst˚ andet fr˚ an P till C 1 . D˚ a vill den ¨ oppna bollen B ϵ ( P ) inte sk¨ ara C 1 . Med andra ord finns bollen i komplementet till C 1 . Detta g¨ aller f¨ or alla punkt i komplementet som d¨ armed ¨ ar en ¨ oppen m¨ angd. F¨ oljdaktligen ¨ ar C 1 en sluten m¨ angd. M¨ angden ¨ ar inte kompakt d˚ a kurvan C 1 inte f˚ ar plats i n˚ agon l˚ ada.
- b) M¨ angden ¨ ar sluten av samma sk¨ al som uppgiften a), och ryms i l˚ adan d¨ ar | x | ≤ 5 och | y | ≤ 5.
- c) M¨ angden ¨ ar begr¨ ansad men ej sluten. Punkten P = ( √ 5 , 5) ¨ ar inte med i m¨ angden C 3 , men varje boll B ϵ ( P ) vill ha en icke-tom sk¨ arning med C 3 . Komplementet till C 3 ¨ ar d¨ arf¨ or inte ¨ oppen, och d˚ a ¨ ar inte C 3 sluten.
- d) Randpunkterna ¨ ar m¨ angden { ( x, y ) | x 2 = y } .

## 2.11.

- a) M¨ angden C 4 i uppgift 2.10 d), till exempel.
- b) M¨ angden R 2 ¨ ar uppenbarligen ¨ oppen, men ocks˚ a sluten! F¨ or att se att R 2 ¨ ar sluten m˚ aste vi visa att komplementet ¨ ar ¨ oppen. Komplementet ¨ ar tomt, och d˚ a blir det inget att kolla.
3. 3.12. Exempelvis r ( θ ) = (2 cos θ, 2 sin θ, -2 cos θ )
4. 3.13. Till exempel (flera alternativ ¨ ar m¨ ojliga):
- a) x = -1 + 2 cos t och y = 2sin t , d¨ ar 0 ≤ t &lt; 2 π .
- b) x = t och y = 3 t +5, d¨ ar 0 ≤ t ≤ 3
- c) x = 2cos θ och y = sin θ , d¨ ar 0 ≤ θ &lt; 2 π

(Ovan ¨ ar parametriseringarna givna koordinat f¨ or koordinat. Det g˚ ar f¨ orst˚ as ocks˚ a bra att uttrycka samma sak med hj¨ alp av en vektorv¨ arda funktioner, t ex i uppgift a:

<!-- formula-not-decoded -->

T¨ ank efter s˚ a att du f¨ orst˚ ar b˚ ada dessa skrivs¨ att och att de ger samma information!)

- 3.14. Ellips. Hastigheten vid t = 2 ¨ ar r ′ (2) = (0 , π ), farten ¨ ar π och accelerationen r ′′ (2) = ( -2 π 2 , 0).
- 3.15. Farten ¨ ar som st¨ orst i punkterna (0 , ± 2) och maxfarten ¨ ar 6 π
- .
- 3.16. Hastighet (1 , 2 , 3). Fart √ 14 m/s. Acceleration (0 , 2 , 6).
- 3.17. Om man v¨ aljer t = 2 och s¨ atter in i parametriseringen f ˚ ar man punkten (2 , 4 , 4) som allts˚ a ligger p˚ a kurvan. En tangentvektor till kurvan i den punkten ¨ ar r ′ (2) = (1 , 4 , 0) s˚ a tangentlinjen kan parametriseras

<!-- formula-not-decoded -->

L¨ angden av den aktuella delen av kurvan ¨ ar ∫ 2 -2 √ 1 + 4 t 2 dt .

## 3.18.

- a) S¨ att in t
2. = 1 i parametriseringen.
- b) Tangentvektor ¨ ar ( x ′ (1) , y ′ (1) , z ′ (1)) = (0 , 2 π, 1).
- c) tangentlinjen kan parametriseras

<!-- formula-not-decoded -->

(H¨ ar ovan ¨ ar parameterformen f¨ or linjen skriven som i Algebra och geometri. Ibland skriver vi bara ( x, y, z ) = (1 , 2 πt, 1 + t ), d˚ a t ∈ R , och menar samma sak som ovan. T¨ ank igenom det h¨ ar s˚ a att du f¨ orst˚ ar att de b˚ ada skrivs¨ atten inneh˚ aller samma information!)

- √ √
- d) L¨ angden ¨ ar ∫ 1 0 1 + 4 π 2 dt = 1 + 4 π 2 .

## 4.19.

- a) Halvplanet { ( x, y ) : x + y &gt; -1 }
- b) Hela R 2
- c) Stripen { ( x, y ) : -3 ≤ y ≤ 1
4. 4.20. Definitionsm¨ angden ¨ ar hela R 2 , v¨ ardem¨ angden ¨ ar alla tal som ¨ ar st¨ orre ¨ an eller lika med -1. Niv˚ akurvorna ¨ ar cirklar runt origo i xy-planet. Grafen ¨ ar en paraboloid (sk˚ alliknande).

```
. }
```

## 4.21.

- a) Niv˚ akurvorna ¨ ar r¨ ata linjer i xy-planet.
- b) Niv˚ akurvorna ¨ ar cirklar runt origo i xy-planet.
- c) Niv˚ aytorna ¨ ar ellipsoider runt origo i xyz-rymden.
4. 4.22. a) 1. b) 1. c) 0. d) Existerar inte. e) 1. Tips f¨ or b) och e): kom ih˚ ag standardgr¨ ansv¨ arden fr˚ an envarre.
5. 4.23. a) Alla punkter i hela R 2 . b) Alla punkter i R 2 utom (0 , 0).
6. 4.24. Exakt samma svar som i uppgift 4.19. 1 Eftersom detta ¨ ar funktioner som ges av element¨ ara uttryck s˚ a ¨ ar de kontinuerliga ¨ overallt d¨ ar de ¨ ar definierade.

1 manuellt insatt referens