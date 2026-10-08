#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define TOTAL_QUESTIONS   25   /* Isany fanontaniana          */
#define QUESTIONS_POSEES  10   /* Isany fanontaniana apetraka */
#define NB_CHOIX           4   /* Isany safidy mipetraka ho safidian'ilay Mpilalao */

/* ---------- Structure an'ilay fanontaniana ---------- */
typedef struct {
    char enonce[256];
    char choix[NB_CHOIX][128];
    int  bonneReponse;
} Question;

/* ---------- fanontaniana ---------- */
static const Question banque[TOTAL_QUESTIONS] = {
    { "Quelle est la capitale de la France ?",
      {"Paris", "Lyon", "Marseille", "Bordeaux"}, 0 },

    { "Combien de bits contient un octet ?",
      {"4", "8", "16", "32"}, 1 },

    { "Qui a cree le langage C ?",
      {"Dennis Ritchie", "Bjarne Stroustrup",
       "Guido van Rossum", "James Gosling"}, 0 },

    { "Quelle planete est la plus proche du Soleil ?",
      {"Venus", "Mars", "Mercure", "La Terre"}, 2 },

    { "Combien font 7 x 8 ?",
      {"48", "54", "56", "64"}, 2 },

    { "En quelle annee l'ONU a-t-elle ete creee ?",
      {"1919", "1945", "1950", "1960"}, 1 },

    { "Quel langage s'execute dans le navigateur cote client ?",
      {"Python", "Java", "JavaScript", "C++"}, 2 },

    { "Quel est le plus grand ocean du monde ?",
      {"L'ocean Pacifique", "L'ocean Atlantique",
       "L'ocean Indien", "L'ocean Arctique"}, 0 },

    { "Quel est le symbole chimique du fer ?",
      {"Fe", "Fr", "F", "Ir"}, 0 },

    { "Qui a ecrit 'Les Miserables' ?",
      {"Emile Zola", "Victor Hugo", "Moliere", "Albert Camus"}, 1 },

    { "Quel est le symbole chimique de l'or ?",
      {"Ag", "Or", "Au", "Go"}, 2 },

    { "Quelle est la racine carree de 144 ?",
      {"10", "12", "14", "16"}, 1 },

    { "Quel protocole est utilise pour naviguer sur le web ?",
      {"FTP", "HTTP", "SMTP", "TCP"}, 1 },

    { "Quelle est la capitale du Japon ?",
      {"Osaka", "Kyoto", "Seoul", "Tokyo"}, 3 },

    { "Combien de joueurs compte une equipe de football sur le terrain ?",
      {"9", "10", "11", "12"}, 2 },

    { "Qui a peint la Joconde ?",
      {"Leonard de Vinci", "Michel-Ange", "Raphael", "Picasso"}, 0 },

    { "Que signifie l'acronyme CPU ?",
      {"Computer Personal Unit", "Central Processing Unit",
       "Central Program Utility", "Control Program Unit"}, 1 },

    { "Quel est le plus grand mammifere du monde ?",
      {"L'elephant d'Afrique", "Le cachalot",
       "La baleine bleue", "La girafe"}, 2 },

    { "Combien de cotes possede un hexagone ?",
      {"5", "6", "7", "8"}, 1 },

    { "Quel est l'element le plus abondant dans l'univers ?",
      {"L'hydrogene", "L'helium", "L'oxygene", "Le carbone"}, 0 },

    { "En quelle annee l'homme a-t-il marche sur la Lune ?",
      {"1959", "1965", "1969", "1972"}, 2 },

    { "Quelle est la langue la plus parlee comme langue maternelle ?",
      {"L'anglais", "L'espagnol", "Le mandarin", "L'hindi"}, 2 },

    { "Que signifie HTML ?",
      {"HyperText Markup Language", "High Tech Modern Language",
       "Home Tool Markup Language", "HyperText Machine Language"}, 0 },

    { "Quel est le plus grand pays du monde par sa superficie ?",
      {"La Chine", "Les Etats-Unis", "Le Canada", "La Russie"}, 3 },

    { "Combien vaut 2 puissance 10 ?",
      {"512", "1000", "1024", "2048"}, 2 }
};

/* ============================================================
 *  Fonctions utilitaires
 * ============================================================ */

/* asany: mi-verifier ny réponse an'ilay utilisateur rehefa mamaly ilay quiz */
static int lireEntier(int min, int max)
{
    char ligne[64];
    int  valeur;

    for (;;) {
        if (fgets(ligne, sizeof ligne, stdin) == NULL)
            continue;                       /* securite : fin de fichier */

        if (sscanf(ligne, "%d", &valeur) == 1 && valeur >= min && valeur <= max)
            return valeur;

        printf("  Choix invalide. Entrez un nombre entre %d et %d : ", min, max);
    }
}

/* asany: mi-verifier ny réponse an'ilay utilisateur rehefa mbola anoy na tsia */
static int lireOuiNon(void)
{
    char ligne[64];

    for (;;) {
        if (fgets(ligne, sizeof ligne, stdin) == NULL)
            continue;

        if (ligne[0] == 'o' || ligne[0] == 'O') return 1;
        if (ligne[0] == 'n' || ligne[0] == 'N') return 0;

        printf("  Repondez par 'o' (oui) ou 'n' (non) : ");
    }
}

/* Manafangaro an'le fanontaniana ao anaty tableau */
static void melanger(int *tab, int n)
{
    int i;

    for (i = n - 1; i > 0; i--) {
        int j   = rand() % (i + 1);
        int tmp = tab[i];
        tab[i]  = tab[j];
        tab[j]  = tmp;
    }
}

/* commentaire any amin'ny farany */
static const char *appreciation(int score)
{
    if (score == QUESTIONS_POSEES) return "Parfait ! Sans faute !";
    if (score >= 8)                return "Excellent !";
    if (score >= 6)                return "Bien joue !";
    if (score >= 4)                return "Pas mal, mais vous pouvez mieux faire.";
    return "Il faut reviser... Courage !";
}

/* ============================================================
 *  Deroulement d'une partie
 * ============================================================ */
static void jouerPartie(void)
{
    int indices[TOTAL_QUESTIONS];
    int score = 0;
    int i, j;

    /* 1. Atao ao anaty tableau ary afangaro */
    for (i = 0; i < TOTAL_QUESTIONS; i++)
        indices[i] = i;

    melanger(indices, TOTAL_QUESTIONS);

    /* 2. Mametraka fanontaniana 10 voalohany */
    for (i = 0; i < QUESTIONS_POSEES; i++) {
        const Question *q = &banque[indices[i]];
        int reponse;

        printf("\n-----------------------------------------------\n");
        printf(" Question %d / %d\n", i + 1, QUESTIONS_POSEES);
        printf("-----------------------------------------------\n");
        printf("%s\n\n", q->enonce);

        for (j = 0; j < NB_CHOIX; j++)
            printf("   %d) %s\n", j + 1, q->choix[j]);

        printf("\nVotre reponse : ");
        reponse = lireEntier(1, NB_CHOIX) - 1;   /* on repasse en 0..3 */

        if (reponse == q->bonneReponse) {
            printf("  >> Bonne reponse !\n");
            score++;
        } else {
            printf("  >> Mauvaise reponse.\n");
            printf("     La bonne reponse etait : %d) %s\n",
                   q->bonneReponse + 1, q->choix[q->bonneReponse]);
        }
    }

    /* 3. Resultat farany */
    printf("\n===============================================\n");
    printf("              RESULTAT FINAL\n");
    printf("===============================================\n");
    printf(" Score : %d / %d\n", score, QUESTIONS_POSEES);
    printf(" %s\n", appreciation(score));
    printf("===============================================\n");
}

/* ============================================================
 *  Programme principal
 * ============================================================ */
int main(void)
{
    /* Avozina ireo fanontaniana */
    srand((unsigned) time(NULL));

    printf("===============================================\n");
    printf("        BIENVENUE DANS LE QUIZ EN C !\n");
    printf("===============================================\n");
    printf(" %d questions vous seront posees, tirees au hasard\n", QUESTIONS_POSEES);
    printf(" parmi une banque de %d questions.\n", TOTAL_QUESTIONS);
    printf(" Repondez en tapant le numero de votre choix (1 a %d).\n", NB_CHOIX);

    do {
        printf("\nAppuyez sur Entree pour commencer...");
        getchar();

        jouerPartie();

        printf("\nVoulez-vous rejouer ? (o/n) : ");
    } while (lireOuiNon());

    printf("\nMerci d'avoir joue ! A bientot.\n");
    return 0;
}