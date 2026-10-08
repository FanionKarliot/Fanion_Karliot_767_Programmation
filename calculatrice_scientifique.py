import math
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # backend Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk,
)


# ===========================================================================
#  THÈME AN'LE APPLICATION
# ===========================================================================
COULEURS = {
    "fond":    "#1c1c1e",
    "panneau": "#242426",
    "ecran":   "#2c2c2e",
    "bordure": "#3a3a3c",
    "texte":   "#ffffff",
    "gris":    "#8e8e93",
    "accent":  "#0a84ff",
    "ok":      "#30d158",
    "warning": "#ff9f0a",
    "danger":  "#ff453a",
}

STYLES_BOUTONS = {
    "chiffre": {"bg": "#3a3a3c", "active": "#4f4f52", "fg": "#ffffff"},
    "fn":      {"bg": "#2c2c2e", "active": "#3d3d40", "fg": "#ffffff"},
    "op":      {"bg": "#ff9f0a", "active": "#ffb340", "fg": "#ffffff"},
    "egal":    {"bg": "#30d158", "active": "#4ade78", "fg": "#ffffff"},
    "effacer": {"bg": "#ff453a", "active": "#ff6961", "fg": "#ffffff"},
}

COULEURS_POINTS = {"racine": "#ff6b6b", "sommet": "#30d158", "origine": "#ff9f0a"}

BOUTONS = [
    [("Rad",  None,   "fn"), ("sin", "sin(", "fn"), ("cos", "cos(", "fn"),
     ("tan", "tan(", "fn"),  ("π",   "pi",   "fn")],
    [("ln",  "ln(",  "fn"),  ("log", "log(", "fn"), ("√", "sqrt(", "fn"),
     ("xʸ",  "**",   "fn"),  ("e",   "e",    "fn")],
    [("(",   "(",    "fn"),  (")",   ")",    "fn"), ("n!", "fact(", "fn"),
     ("1/x", "1/(",  "fn"),  ("mod", "%",    "fn")],
    [("7", "7", "chiffre"), ("8", "8", "chiffre"), ("9", "9", "chiffre"),
     ("÷", "/", "op"),      ("C", None, "effacer")],
    [("4", "4", "chiffre"), ("5", "5", "chiffre"), ("6", "6", "chiffre"),
     ("×", "*", "op"),      ("⌫", None, "effacer")],
    [("1", "1", "chiffre"), ("2", "2", "chiffre"), ("3", "3", "chiffre"),
     ("−", "-", "op"),      ("Ans", "Ans", "fn")],
    [("0", "0", "chiffre"), (".", ".", "chiffre"), ("±", None, "fn"),
     ("+", "+", "op"),      ("=", None, "egal")],
]


# ===========================================================================
#  fONCTION MI-CALCUL NOMBRE AM'MATHEMATIQUE 
# ===========================================================================
def namespace_scalaire(degres=False):
    """Fonctions mathématiques pour l'évaluation scalaire (calculatrice)."""
    if degres:
        sin = lambda v: math.sin(math.radians(v))
        cos = lambda v: math.cos(math.radians(v))
        tan = lambda v: math.tan(math.radians(v))
        asin = lambda v: math.degrees(math.asin(v))
        acos = lambda v: math.degrees(math.acos(v))
        atan = lambda v: math.degrees(math.atan(v))
    else:
        sin, cos, tan = math.sin, math.cos, math.tan
        asin, acos, atan = math.asin, math.acos, math.atan

    return {
        "pi": math.pi, "e": math.e,
        "sin": sin, "cos": cos, "tan": tan,
        "asin": asin, "acos": acos, "atan": atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "exp": math.exp, "ln": math.log, "log": math.log10,
        "log10": math.log10, "log2": math.log2,
        "sqrt": math.sqrt, "abs": abs, "round": round,
        "floor": math.floor, "ceil": math.ceil,
        "fact": lambda n: math.factorial(int(n)),
    }


def namespace_tableau(degres=False):
    """Fonctions vectorisées pour le tracé de courbes."""
    if degres:
        sin = lambda v: np.sin(np.radians(v))
        cos = lambda v: np.cos(np.radians(v))
        tan = lambda v: np.tan(np.radians(v))
        asin = lambda v: np.degrees(np.arcsin(v))
        acos = lambda v: np.degrees(np.arccos(v))
        atan = lambda v: np.degrees(np.arctan(v))
    else:
        sin, cos, tan = np.sin, np.cos, np.tan
        asin, acos, atan = np.arcsin, np.arccos, np.arctan

    def fact(v):
        return np.vectorize(math.gamma)(np.asarray(v, dtype=float) + 1.0)

    return {
        "pi": np.pi, "e": np.e,
        "sin": sin, "cos": cos, "tan": tan,
        "asin": asin, "acos": acos, "atan": atan,
        "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
        "exp": np.exp, "ln": np.log, "log": np.log10,
        "log10": np.log10, "log2": np.log2,
        "sqrt": np.sqrt, "abs": np.abs,
        "floor": np.floor, "ceil": np.ceil, "fact": fact,
    }

# FORMATAGENA VALEUR AM'MATHEMATIQUE
def formater(valeur):
    """Chaîne lisible pour un résultat numérique."""
    if isinstance(valeur, bool):
        return str(valeur)
    if isinstance(valeur, (int, np.integer)):
        return str(int(valeur))
    if isinstance(valeur, (float, np.floating)):
        valeur = float(valeur)
        if math.isnan(valeur) or math.isinf(valeur):
            return str(valeur)
        if valeur.is_integer() and abs(valeur) < 1e16:
            return str(int(valeur))
        return f"{valeur:.12g}"
    return str(valeur)


# ===========================================================================
#  ONGLET 1 — APPLICATION MOMBAN'NY CALCULATRICE 
# ===========================================================================
class OngletCalculatrice(ttk.Frame):
    """Clavier scientifique + historique + envoi vers le graphique."""

    def __init__(self, parent, app):
        super().__init__(parent, style="Fond.TFrame")
        self.app = app

        self.var_expression = tk.StringVar()
        self.var_statut = tk.StringVar(value="Mode : Radians")
        self.bouton_mode = None
        self.historique = []  # liste de (expression, résultat formaté)

        self._construire()
        self._maj_mode()
        self._maj_historique()

    # ------------------------------------------------------------------
    def _construire(self):
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        calc = ttk.Frame(self, style="Fond.TFrame")
        calc.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        hist = ttk.Frame(self, style="Fond.TFrame")
        hist.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        self._construire_calculatrice(calc)
        self._construire_historique(hist)

    def _construire_calculatrice(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        # --- Écran an'le calculatrice ---
        ecran = tk.Frame(parent, bg=COULEURS["ecran"])
        ecran.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.entry_expression = tk.Entry(
            ecran, textvariable=self.var_expression,
            font=("Consolas", 26), bg=COULEURS["ecran"], fg=COULEURS["texte"],
            bd=0, justify="right", insertbackground=COULEURS["texte"],
        )
        self.entry_expression.pack(fill="x", padx=14, pady=(16, 4))
        self.entry_expression.bind("<Return>", self.calculer)
        self.entry_expression.bind("<KP_Enter>", self.calculer)
        self.entry_expression.bind("<Escape>", lambda e: self.effacer())

        tk.Label(ecran, textvariable=self.var_statut, bg=COULEURS["ecran"],
                 fg=COULEURS["gris"], font=("Segoe UI", 10),
                 anchor="e").pack(fill="x", padx=14, pady=(0, 12))

        # --- Grille ana boutons afaka kitihana ---
        grille = ttk.Frame(parent, style="Fond.TFrame")
        grille.grid(row=1, column=0, sticky="nsew")

        for c in range(5):
            grille.columnconfigure(c, weight=1, uniform="btn")
        for r in range(len(BOUTONS)):
            grille.rowconfigure(r, weight=1, uniform="btn")

        for i, ligne in enumerate(BOUTONS):
            for j, (texte, insertion, style) in enumerate(ligne):
                action = self._action_bouton(texte, insertion)
                bouton = self._creer_bouton(grille, texte, action, i, j,
                                            STYLES_BOUTONS[style])
                if texte == "Rad":
                    self.bouton_mode = bouton

        # --- Barre an'actions (Mandefa / mi-vider) ---
        barre = ttk.Frame(parent, style="Fond.TFrame")
        barre.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        barre.columnconfigure(0, weight=1)
        barre.columnconfigure(1, weight=1)

        tk.Button(barre, text="📈 Envoyer au graphique",
                  command=self._envoyer_graphique,
                  bg=COULEURS["accent"], fg="white",
                  activebackground="#3d9bff", activeforeground="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                  cursor="hand2").grid(row=0, column=0, sticky="ew",
                                       padx=(0, 3), ipady=6)
        tk.Button(barre, text="🗑 Vider l'historique",
                  command=self._vider_historique,
                  bg=COULEURS["panneau"], fg=COULEURS["texte"],
                  activebackground="#3a3a3c", activeforeground="white",
                  font=("Segoe UI", 10), relief="flat", bd=0,
                  cursor="hand2").grid(row=0, column=1, sticky="ew",
                                       padx=(3, 0), ipady=6)

    def _construire_historique(self, parent):
        ttk.Label(parent, text="Historique",
                  style="Titre.TLabel").pack(anchor="w", pady=(0, 6))

        cadre = tk.Frame(parent, bg=COULEURS["panneau"])
        cadre.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(cadre, orient="vertical")
        self.liste_hist = tk.Listbox(
            cadre, yscrollcommand=sb.set, bg=COULEURS["panneau"],
            fg=COULEURS["texte"], selectbackground=COULEURS["accent"],
            selectforeground="white", bd=0, highlightthickness=0,
            font=("Consolas", 10), activestyle="none",
        )
        sb.config(command=self.liste_hist.yview)
        sb.pack(side="right", fill="y")
        self.liste_hist.pack(fill="both", expand=True, padx=4, pady=4)
        self.liste_hist.bind("<Double-Button-1>", self._reutiliser_historique)
        self.liste_hist.bind("<Return>", self._reutiliser_historique)

    def _creer_bouton(self, parent, texte, action, ligne, colonne, style):
        b = tk.Button(
            parent, text=texte, command=action,
            bg=style["bg"], fg=style["fg"],
            activebackground=style["active"], activeforeground=style["fg"],
            font=("Segoe UI", 14), relief="flat", bd=0,
            highlightthickness=0, cursor="hand2",
        )
        b.grid(row=ligne, column=colonne, sticky="nsew", padx=3, pady=3)
        return b

    def _action_bouton(self, texte, insertion):
        if texte == "Rad":
            return self.app.basculer_mode
        if texte == "C":
            return self.effacer
        if texte == "⌫":
            return self.retour
        if texte == "=":
            return self.calculer
        if texte == "±":
            return self.plus_moins
        # Manandanja ao am'le app : capture de `insertion` par défaut (late-binding fix)
        return lambda t=insertion: self.inserer(t)

    # ------------------------------------------------------------------
    def _maj_mode(self):
        mode = "Degrés" if self.app.degres.get() else "Radians"
        self.var_statut.set(f"Mode : {mode}")
        if self.bouton_mode is not None:
            self.bouton_mode.config(
                text="Deg" if self.app.degres.get() else "Rad")

    def inserer(self, texte):
        self.var_expression.set(self.var_expression.get() + texte)
        self.entry_expression.icursor("end")
        self.var_statut.set("")

    def effacer(self):
        self.var_expression.set("")
        self.var_statut.set("")
        self.entry_expression.focus_set()

    def retour(self):
        self.var_expression.set(self.var_expression.get()[:-1])
        self.entry_expression.icursor("end")

    def plus_moins(self):
        expr = self.var_expression.get()
        if expr.startswith("-"):
            self.var_expression.set(expr[1:])
        elif expr:
            self.var_expression.set("-" + expr)
        self.entry_expression.icursor("end")

    def calculer(self, event=None):
        expr = self.var_expression.get().strip()
        if not expr:
            return
        expr_eval = expr.replace("^", "**")

        try:
            ns = namespace_scalaire(self.app.degres.get())
            ns["Ans"] = self.app.ans
            resultat = eval(expr_eval, {"__builtins__": {}}, ns)
        except ZeroDivisionError:
            self._afficher_erreur("Division par zéro"); return
        except (SyntaxError, TypeError):
            self._afficher_erreur("Syntaxe invalide"); return
        except (ValueError, OverflowError):
            self._afficher_erreur("Valeur hors domaine"); return
        except NameError:
            self._afficher_erreur("Nom inconnu"); return
        except Exception:
            self._afficher_erreur("Erreur de calcul"); return

        self.app.ans = float(resultat) if not isinstance(resultat, bool) else resultat
        res_txt = formater(resultat)
        self.var_expression.set(res_txt)
        self.entry_expression.icursor("end")
        self.var_statut.set(f"Ans = {res_txt}")

        self.historique.append((expr, res_txt))
        self._maj_historique()

    def _afficher_erreur(self, message):
        self.var_statut.set(f"⚠ {message}")
        self.bell()

    def _maj_historique(self):
        self.liste_hist.delete(0, "end")
        for e, r in reversed(self.historique[-200:]):
            self.liste_hist.insert("end", f"{e} = {r}")

    def _reutiliser_historique(self, event=None):
        sel = self.liste_hist.curselection()
        if not sel:
            return
        index = len(self.historique) - 1 - sel[0]
        expr, _ = self.historique[index]
        self.var_expression.set(expr)
        self.entry_expression.icursor("end")
        self.entry_expression.focus_set()

    def _vider_historique(self):
        self.historique.clear()
        self._maj_historique()

    def _envoyer_graphique(self):
        expr = self.var_expression.get().strip()
        if not expr:
            return
        self.app.onglet_graphique.var_fx.set(expr)
        self.app.onglets.select(1)  # ahafahana mandaha ao am'onglet Graphique
        self.app.onglet_graphique.tracer(reinit=True)


# ===========================================================================
#  ONGLET 2 — APPLICATION MOMBAN'NY GRAPHIQUE LIBRE INTERACTIF
# ===========================================================================
class BarreOutilsGraphique(NavigationToolbar2Tk):
    """Barre d'outils dont le bouton Home réinitialise la vue de notre onglet."""

    def __init__(self, canvas, parent, onglet):
        self.onglet = onglet
        super().__init__(canvas, parent, pack_toolbar=False)

    def home(self, *args):
        self.onglet.tracer(reinit=True)

    def set_message(self, s):   # ampiasaina ny barre d'état teo aloha ihany
        pass


class OngletGraphique(ttk.Frame):
    """Traceur d'expressions libres, avec zoom/pan/suivi."""

    def __init__(self, parent, app):
        super().__init__(parent, style="Fond.TFrame")
        self.app = app

        self.var_fx = tk.StringVar(value="sin(x) * exp(-x/5)")
        self.var_xmin = tk.StringVar(value="-10")
        self.var_xmax = tk.StringVar(value="10")

        self.figure = None
        self.axe = None
        self.canvas = None
        self.ligne = None
        self.suivi = None
        self.suivi_txt = None
        self._pan = None
        self._expr_courante = None

        self._construire()
        self.after(150, lambda: self.tracer(reinit=True))

    # ------------------------------------------------------------------
    def _construire(self):
        # --- Barre d'entrée ao am'Application ---
        haut = ttk.Frame(self, style="Fond.TFrame")
        haut.pack(fill="x", padx=12, pady=(12, 6))
        haut.columnconfigure(1, weight=1)

        ttk.Label(haut, text="f(x) =", style="TLabel",
                  font=("Consolas", 13)).grid(row=0, column=0, padx=(0, 6))

        entree_fx = tk.Entry(haut, textvariable=self.var_fx,
                             font=("Consolas", 13), bg=COULEURS["ecran"],
                             fg=COULEURS["texte"], bd=0,
                             insertbackground=COULEURS["texte"])
        entree_fx.grid(row=0, column=1, columnspan=4, sticky="ew",
                       ipady=6, padx=4, pady=4)
        entree_fx.bind("<Return>", lambda e: self.tracer(reinit=True))

        ttk.Label(haut, text="x min", style="Gris.TLabel").grid(
            row=1, column=0, sticky="e")
        tk.Entry(haut, textvariable=self.var_xmin, width=8,
                 font=("Consolas", 11), bg=COULEURS["ecran"],
                 fg=COULEURS["texte"], bd=0, justify="center",
                 insertbackground=COULEURS["texte"]).grid(
            row=1, column=1, ipady=4, padx=4, pady=4, sticky="w")

        ttk.Label(haut, text="x max", style="Gris.TLabel").grid(
            row=1, column=2, sticky="e")
        tk.Entry(haut, textvariable=self.var_xmax, width=8,
                 font=("Consolas", 11), bg=COULEURS["ecran"],
                 fg=COULEURS["texte"], bd=0, justify="center",
                 insertbackground=COULEURS["texte"]).grid(
            row=1, column=3, ipady=4, padx=4, pady=4, sticky="w")

        tk.Button(haut, text="Tracer", command=lambda: self.tracer(reinit=True),
                  bg=COULEURS["accent"], fg="white",
                  activebackground="#3d9bff", activeforeground="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", bd=0,
                  cursor="hand2").grid(row=1, column=4, sticky="ew",
                                       padx=6, ipady=4)

        # --- Figuren'ilay graphe ---
        cadre_figure = ttk.Frame(self, style="Fond.TFrame")
        cadre_figure.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        self.figure = Figure(figsize=(6, 5), dpi=100,
                             facecolor=COULEURS["fond"])
        self.axe = self.figure.add_subplot(111)
        self._styliser_axe()

        self.canvas = FigureCanvasTkAgg(self.figure, master=cadre_figure)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = BarreOutilsGraphique(self.canvas, cadre_figure, self)
        self.toolbar.update()
        self.toolbar.pack(fill="x")

        # --- Barre d'état ---
        self.status = ttk.Label(
            self,
            text="Molette : zoom  |  Clic gauche + glisser : déplacer  |  "
                 "Double-clic : réinitialiser",
            style="Gris.TLabel", anchor="w", font=("Consolas", 9))
        self.status.pack(fill="x", padx=12, pady=(0, 6))

        # --- Interactions ---
        self.canvas.mpl_connect("scroll_event", self._on_scroll)
        self.canvas.mpl_connect("button_press_event", self._on_press)
        self.canvas.mpl_connect("button_release_event", self._on_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)

    def _styliser_axe(self):
        self.axe.set_facecolor("#242426")
        self.axe.tick_params(colors=COULEURS["gris"], labelsize=9)
        self.axe.xaxis.label.set_color(COULEURS["gris"])
        self.axe.yaxis.label.set_color(COULEURS["gris"])
        self.axe.title.set_color(COULEURS["texte"])
        for epine in self.axe.spines.values():
            epine.set_color("#3a3a3c")

    # ------------------------------------------------------------------
    def tracer(self, reinit=True):
        expr = self.var_fx.get().strip()
        if not expr:
            return
        expr_eval = expr.replace("^", "**")

        # Bornes entre ny [xmin; xmax]
        if reinit:
            try:
                xmin = float(self.var_xmin.get().replace(",", "."))
                xmax = float(self.var_xmax.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erreur", "Bornes de x invalides.")
                return
            if xmin >= xmax:
                messagebox.showerror("Erreur", "x min doit être < x max.")
                return
        else:
            xmin, xmax = self.axe.get_xlim()

        # Évaluation ai amin'ilay application
        ns = namespace_tableau(self.app.degres.get())
        ns["x"] = np.linspace(xmin, xmax, 2000)

        try:
            with np.errstate(all="ignore"):
                y = eval(expr_eval, {"__builtins__": {}}, ns)
            y = np.broadcast_to(np.asarray(y, dtype=float),
                                ns["x"].shape).astype(float)
        except Exception as e:
            messagebox.showerror("Erreur",
                                 f"Impossible de tracer f(x) :\n{e}")
            return

        self._expr_courante = expr_eval

        # --- Traçage an'le graphe ---
        self.axe.clear()
        self._styliser_axe()
        self.ligne, = self.axe.plot(ns["x"], y, color=COULEURS["accent"],
                                     linewidth=2, label=f"f(x) = {expr}")
        self.axe.axhline(0, color="#8e8e93", linewidth=0.8)
        self.axe.axvline(0, color="#8e8e93", linewidth=0.8)
        self.axe.grid(True, color="#3a3a3c", linestyle="--", linewidth=0.5)
        self.axe.set_xlim(xmin, xmax)
        self.axe.set_title(f"f(x) = {expr}", color=COULEURS["texte"], fontsize=11)
        self.axe.legend(loc="upper left", fontsize=9, framealpha=0.85)

        # Cadrage automatique en y ao am'le graphe
        finis = y[np.isfinite(y)]
        if finis.size:
            lo, hi = np.percentile(finis, [2, 98])
            if hi - lo < 1e-9:
                lo, hi = lo - 1.0, hi + 1.0
            marge = 0.1 * (hi - lo)
            self.axe.set_ylim(lo - marge, hi + marge)

        # Point mouvant (suivi du curseur)
        self.suivi, = self.axe.plot([], [], "o", color="#ff9800",
                                     markersize=8, markeredgecolor="black",
                                     zorder=8)
        self.suivi_txt = self.axe.annotate(
            "", xy=(0, 0), xytext=(12, -22), textcoords="offset points",
            fontsize=10, zorder=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white",
                      ec="#999999", alpha=0.95))
        self.suivi.set_visible(False)
        self.suivi_txt.set_visible(False)

        # Recalcul an'le courbe rehefa miova ny zoom
        self.axe.callbacks.connect("xlim_changed", self._on_xlim_changed)

        self.canvas.draw_idle()

    def _on_xlim_changed(self, _ax):
        """Recalcule la courbe sur la zone visible (courbe infinie)."""
        if self.ligne is None or not self._expr_courante:
            return
        x0, x1 = self.axe.get_xlim()
        marge = (x1 - x0) * 0.05
        x = np.linspace(x0 - marge, x1 + marge, 3000)
        ns = namespace_tableau(self.app.degres.get())
        ns["x"] = x
        try:
            with np.errstate(all="ignore"):
                y = eval(self._expr_courante, {"__builtins__": {}}, ns)
            y = np.broadcast_to(np.asarray(y, dtype=float), x.shape).astype(float)
        except Exception:
            return
        self.ligne.set_data(x, y)

    # ------------------------------------------------------------------
    #  Interactions souris sy point de suivi an le souris
    # ------------------------------------------------------------------
    def _on_scroll(self, event):
        if event.inaxes is not self.axe or event.xdata is None:
            return
        f = 1 / 1.2 if event.button == "up" else 1.2
        xd, yd = event.xdata, event.ydata
        x0, x1 = self.axe.get_xlim()
        y0, y1 = self.axe.get_ylim()
        nx0, nx1 = xd - (xd - x0) * f, xd + (x1 - xd) * f
        ny0, ny1 = yd - (yd - y0) * f, yd + (y1 - yd) * f
        if 1e-9 < nx1 - nx0 < 1e9:
            self.axe.set_xlim(nx0, nx1)
        if 1e-9 < ny1 - ny0 < 1e9:
            self.axe.set_ylim(ny0, ny1)
        self.canvas.draw_idle()

    def _on_press(self, event):
        if event.inaxes is not self.axe:
            return
        if event.dblclick:
            self.tracer(reinit=True)
            return
        if event.button != 1 or self.toolbar.mode != "":
            return
        self._pan = {"px": event.x, "py": event.y,
                     "xlim": self.axe.get_xlim(),
                     "ylim": self.axe.get_ylim()}
        self.canvas.get_tk_widget().config(cursor="fleur")

    def _on_release(self, event):
        self._pan = None
        self.canvas.get_tk_widget().config(cursor="")

    def _on_motion(self, event):
        # Pan en cours
        if self._pan is not None and event.x is not None:
            p = self._pan
            bbox = self.axe.bbox
            dx = (event.x - p["px"]) * (p["xlim"][1] - p["xlim"][0]) / bbox.width
            dy = (event.y - p["py"]) * (p["ylim"][1] - p["ylim"][0]) / bbox.height
            self.axe.set_xlim(p["xlim"][0] - dx, p["xlim"][1] - dx)
            self.axe.set_ylim(p["ylim"][0] - dy, p["ylim"][1] - dy)
            self.canvas.draw_idle()
            return

        # Suivi an'le curseur
        if event.inaxes is self.axe and event.xdata is not None and self.suivi is not None:
            x = event.xdata
            try:
                ns = namespace_tableau(self.app.degres.get())
                ns["x"] = np.array([x])
                with np.errstate(all="ignore"):
                    y = float(np.asarray(eval(self._expr_courante,
                                              {"__builtins__": {}}, ns)).ravel()[0])
            except Exception:
                y = float("nan")
            if math.isfinite(y):
                self.suivi.set_data([x], [y])
                self.suivi_txt.xy = (x, y)
                self.suivi_txt.set_text(f"({x:.3f} ; {y:.3f})")
                self.suivi.set_visible(True)
                self.suivi_txt.set_visible(True)
                self.status.config(text=f"x = {x:.4f}     f(x) = {y:.4f}")
            else:
                self.suivi.set_visible(False)
                self.suivi_txt.set_visible(False)
                self.status.config(text=f"x = {x:.4f}     f(x) non défini")
            self.canvas.draw_idle()
        elif self.suivi is not None and self.suivi.get_visible():
            self.suivi.set_visible(False)
            self.suivi_txt.set_visible(False)
            self.status.config(
                text="Molette : zoom  |  Clic gauche + glisser : déplacer  |  "
                     "Double-clic : réinitialiser")
            self.canvas.draw_idle()


# ===========================================================================
#  ONGLET 3 — APPLICATION MOMBAN'NY ANALYSE DE FONCTIONS PARAMÉTRIQUES
# ===========================================================================
TYPES = [
    ("Affine : f(x) = ax + b", "affine"),
    ("Polynôme : f(x) = ax² + bx + c", "polynome"),
    ("Exponentielle : f(x) = a·e^(bx) + c", "exponentielle"),
    ("Logarithme : f(x) = a·ln(bx) + c", "logarithme"),
]

CHAMPS = {
    "affine":        [("a", "1"), ("b", "0")],
    "polynome":      [("a", "1"), ("b", "0"), ("c", "0")],
    "exponentielle": [("a", "1"), ("b", "1"), ("c", "0")],
    "logarithme":    [("a", "1"), ("b", "1"), ("c", "0")],
}


class OngletAnalyse(ttk.Frame):
    """Résolveur de fonctions paramétriques (racines, sommet, asymptotes)."""

    def __init__(self, parent, app):
        super().__init__(parent, style="Fond.TFrame")
        self.app = app

        self.type_fonction = tk.StringVar(value="affine")
        self.coeffs = {}

        self.affiche = False
        self._type_courant = "affine"
        self._c_courant = {"a": 1.0, "b": 0.0}
        self._pan = None
        self.ligne = None
        self.suivi = None
        self.suivi_txt = None

        self._creer_interface()
        self.after(180, self._maj_champs)

    # ------------------------------------------------------------------
    def _creer_interface(self):
        panneau = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panneau.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        gauche = ttk.Frame(panneau, width=360, style="Fond.TFrame")
        droite = ttk.Frame(panneau, style="Fond.TFrame")
        panneau.add(gauche, weight=0)
        panneau.add(droite, weight=1)

        # ---------------- Panneau gauche ----------------
        ttk.Label(gauche, text="Type de fonction",
                  style="Titre.TLabel", font=("Segoe UI", 13, "bold")
                  ).pack(pady=(10, 6), anchor="w", padx=12)

        for texte, val in TYPES:
            ttk.Radiobutton(gauche, text=texte, variable=self.type_fonction,
                            value=val, command=self._maj_champs
                            ).pack(anchor="w", padx=15, pady=3)

        self.frame_coeffs = ttk.LabelFrame(
            gauche, text="Coefficients (modifiables en direct)")
        self.frame_coeffs.pack(fill=tk.X, padx=10, pady=(12, 6))

        frame_int = ttk.LabelFrame(gauche, text="Intervalle initial")
        frame_int.pack(fill=tk.X, padx=10, pady=6)
        ttk.Label(frame_int, text="x min :").grid(row=0, column=0,
                                                   padx=5, pady=4, sticky="e")
        self.entry_xmin = ttk.Entry(frame_int, width=10)
        self.entry_xmin.insert(0, "-10")
        self.entry_xmin.grid(row=0, column=1, padx=5)
        ttk.Label(frame_int, text="x max :").grid(row=1, column=0,
                                                   padx=5, pady=4, sticky="e")
        self.entry_xmax = ttk.Entry(frame_int, width=10)
        self.entry_xmax.insert(0, "10")
        self.entry_xmax.grid(row=1, column=1, padx=5)
        for e in (self.entry_xmin, self.entry_xmax):
            e.bind("<Return>", lambda ev: self.tracer(reinit=True))

        tk.Button(gauche, text="🔍 Tracer / Réinitialiser",
                  bg=COULEURS["ok"], fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", bd=0,
                  cursor="hand2",
                  command=lambda: self.tracer(reinit=True)
                  ).pack(fill=tk.X, padx=10, pady=(10, 4), ipady=4)
        tk.Button(gauche, text="↕ Ajuster l'axe Y",
                  bg=COULEURS["accent"], fg="white",
                  font=("Segoe UI", 10), relief="flat", bd=0,
                  cursor="hand2", command=self.ajuster_y
                  ).pack(fill=tk.X, padx=10, pady=4, ipady=3)
        tk.Button(gauche, text="🗑 Effacer le graphe",
                  bg=COULEURS["danger"], fg="white",
                  font=("Segoe UI", 10), relief="flat", bd=0,
                  cursor="hand2", command=self.effacer
                  ).pack(fill=tk.X, padx=10, pady=4, ipady=3)

        frame_res = ttk.LabelFrame(gauche, text="Résultats")
        frame_res.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.txt = tk.Text(frame_res, height=10, width=38, wrap="word",
                           bg=COULEURS["panneau"], fg=COULEURS["texte"],
                           insertbackground=COULEURS["texte"],
                           font=("Consolas", 10), state="disabled",
                           relief="flat", bd=0)
        sb = ttk.Scrollbar(frame_res, command=self.txt.yview)
        self.txt.config(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ---------------- Panneau droit ----------------
        self.figure = Figure(figsize=(8, 6), dpi=100,
                             facecolor=COULEURS["fond"])
        self.canvas = FigureCanvasTkAgg(self.figure, master=droite)
        self.toolbar = BarreOutilsAnalyse(self.canvas, droite, self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.status = ttk.Label(
            droite,
            text="Molette : zoom  |  Clic gauche + glisser : déplacer  |  "
                 "Double-clic : réinitialiser",
            style="Gris.TLabel", anchor="w", font=("Consolas", 9))
        self.status.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=3)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ax = None
        self._axes_vides()

        self.canvas.mpl_connect("scroll_event", self._on_scroll)
        self.canvas.mpl_connect("button_press_event", self._on_press)
        self.canvas.mpl_connect("button_release_event", self._on_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)

    def _maj_champs(self):
        for w in self.frame_coeffs.winfo_children():
            w.destroy()
        self.coeffs.clear()

        for i, (cle, defaut) in enumerate(CHAMPS[self.type_fonction.get()]):
            ttk.Label(self.frame_coeffs, text=f"{cle} :",
                      font=("Segoe UI", 11)
                      ).grid(row=i, column=0, padx=8, pady=5, sticky="e")
            sp = ttk.Spinbox(self.frame_coeffs, from_=-1000, to=1000,
                             increment=0.1, format="%.2f", width=12,
                             font=("Segoe UI", 11),
                             command=lambda: self.tracer(reinit=False,
                                                          silent=True))
            sp.set(defaut)
            sp.grid(row=i, column=1, padx=5, pady=5)
            sp.bind("<KeyRelease>",
                    lambda ev: self.tracer(reinit=False, silent=True))
            self.coeffs[cle] = sp

        self.tracer(reinit=True)

    def _ecrire_resultat(self, texte):
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", texte)
        self.txt.config(state="disabled")

    # ------------------------------------------------------------------
    #  Mathématiques sy analyse de fonction
    # ------------------------------------------------------------------
    def _get_coeffs(self, silent=False):
        try:
            c = {k: float(v.get().replace(",", "."))
                 for k, v in self.coeffs.items()}
            if not all(np.isfinite(list(c.values()))):
                raise ValueError
            return c
        except ValueError:
            if not silent:
                messagebox.showerror("Erreur",
                                     "Veuillez entrer des nombres valides.")
            return None

    @staticmethod
    def _evaluer(x, type_f, c):
        x = np.asarray(x, dtype=float)
        with np.errstate(all="ignore"):
            if type_f == "affine":
                y = c["a"] * x + c["b"]
            elif type_f == "polynome":
                y = c["a"] * x ** 2 + c["b"] * x + c["c"]
            elif type_f == "exponentielle":
                y = c["a"] * np.exp(c["b"] * x) + c["c"]
            else:
                y = c["a"] * np.log(c["b"] * x) + c["c"]
        return np.where(np.isfinite(y), y, np.nan)

    @staticmethod
    def _expression(type_f, c):
        a, b, cc = c["a"], c["b"], c.get("c", 0.0)

        def s(v):
            return f"+ {v:g}" if v >= 0 else f"- {abs(v):g}"

        if type_f == "affine":
            return f"{a:g}x {s(b)}"
        if type_f == "polynome":
            return f"{a:g}x² {s(b)}x {s(cc)}"
        if type_f == "exponentielle":
            return f"{a:g}·e^({b:g}x) {s(cc)}"
        return f"{a:g}·ln({b:g}x) {s(cc)}"

    def _analyser(self, type_f, c):
        a, b, cc = c["a"], c["b"], c.get("c", 0.0)
        t = [f"f(x) = {self._expression(type_f, c)}", ""]
        points = []
        asym_h = asym_v = None

        def f(x):
            return float(self._evaluer(x, type_f, c))

        if type_f == "affine":
            if a == 0:
                t.append("a = 0 : fonction constante")
                t.append("f(x) = 0 pour tout x" if b == 0
                         else "f(x) = 0 : aucune solution")
            else:
                x0 = -b / a
                points.append(("racine", x0, 0.0))
                t += ["Résolution de f(x) = 0 :",
                      f"  x = -b/a = {x0:.4f}", "",
                      f"Pente : {a:g} "
                      f"({'croissante ↗' if a > 0 else 'décroissante ↘'})"]
            t.append(f"Ordonnée à l'origine : {b:g}")
            points.append(("origine", 0.0, b))

        elif type_f == "polynome":
            if a == 0:
                t.append("a = 0 : fonction affine ou constante")
                if b != 0:
                    x0 = -cc / b
                    points.append(("racine", x0, 0.0))
                    t.append(f"  x = {x0:.4f}")
                else:
                    t.append("f(x) = 0 pour tout x" if cc == 0
                             else "f(x) = 0 : aucune solution")
            else:
                delta = b * b - 4 * a * cc
                t += [f"Discriminant Δ = {delta:.4f}", ""]
                if delta > 0:
                    r = np.sqrt(delta)
                    x1, x2 = (-b - r) / (2 * a), (-b + r) / (2 * a)
                    t += ["Δ > 0 → 2 solutions :",
                          f"  x₁ = {x1:.4f}", f"  x₂ = {x2:.4f}"]
                    points += [("racine", x1, 0.0), ("racine", x2, 0.0)]
                elif delta == 0:
                    x0 = -b / (2 * a)
                    t += ["Δ = 0 → 1 solution double :", f"  x = {x0:.4f}"]
                    points.append(("racine", x0, 0.0))
                else:
                    t.append("Δ < 0 → aucune solution réelle")
                xs = -b / (2 * a)
                ys = f(xs)
                t += ["", f"Sommet : ({xs:.4f} ; {ys:.4f})",
                      "Parabole ouverte vers le haut ∪" if a > 0
                      else "Parabole ouverte vers le bas ∩"]
                points.append(("sommet", xs, ys))
            points.append(("origine", 0.0, cc))

        elif type_f == "exponentielle":
            if a == 0:
                t.append(f"a = 0 : fonction constante = {cc:g}")
            elif b == 0:
                t.append(f"b = 0 : fonction constante = {a + cc:g}")
            else:
                asym_h = cc
                if -cc / a > 0:
                    x0 = np.log(-cc / a) / b
                    t += ["Résolution de f(x) = 0 :",
                          "  e^(bx) = -c/a",
                          f"  x = ln(-c/a)/b = {x0:.4f}"]
                    points.append(("racine", x0, 0.0))
                else:
                    t.append("f(x) = 0 : aucune solution réelle (e^(bx) > 0)")
                t += ["",
                      "Croissante ↗" if a * b > 0 else "Décroissante ↘",
                      f"Asymptote horizontale : y = {cc:g}"]
                points.append(("origine", 0.0, a + cc))

        else:  # fonction logarithme
            if b == 0:
                t.append("b = 0 : ln(bx) n'est pas défini")
            else:
                t.append("Domaine : x > 0" if b > 0 else "Domaine : x < 0")
                if a == 0:
                    t.append(f"a = 0 : fonction constante = {cc:g}")
                else:
                    asym_v = 0.0
                    with np.errstate(all="ignore"):
                        x0 = np.exp(-cc / a) / b
                    t.append("")
                    if np.isfinite(x0) and x0 != 0:
                        t += ["Résolution de f(x) = 0 :",
                              "  x = e^(-c/a) / b", f"  x = {x0:.4f}"]
                        points.append(("racine", x0, 0.0))
                    else:
                        t.append("Solution non représentable")
                    t += ["",
                          "Croissante ↗" if a * b > 0 else "Décroissante ↘",
                          "Asymptote verticale : x = 0"]

        return {"texte": "\n".join(t), "points": points,
                "asym_h": asym_h, "asym_v": asym_v,
                "expr": self._expression(type_f, c)}

    # ------------------------------------------------------------------
    #  Traçage an'le courbe
    # ------------------------------------------------------------------
    def _style_axes(self, ax):
        ax.set_facecolor("#242426")
        ax.minorticks_on()
        ax.tick_params(colors=COULEURS["gris"], labelsize=9)
        ax.grid(True, which="major", color="#3a3a3c", alpha=0.5)
        ax.grid(True, which="minor", color="#3a3a3c", alpha=0.2)
        ax.axhline(0, color=COULEURS["gris"], linewidth=1.0, zorder=2)
        ax.axvline(0, color=COULEURS["gris"], linewidth=1.0, zorder=2)
        ax.set_xlabel("x", color=COULEURS["gris"], fontsize=11)
        ax.set_ylabel("f(x)", color=COULEURS["gris"], fontsize=11)
        for sp in ax.spines.values():
            sp.set_color("#3a3a3c")

    def _axes_vides(self):
        self.figure.clf()
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.08, right=0.97,
                                    top=0.92, bottom=0.09)
        self._style_axes(self.ax)
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_title("Graphe de la fonction",
                          color=COULEURS["texte"], fontsize=12)

    def _construire_axes(self, type_f, c, info, xlim, ylim):
        self.figure.clf()
        self.ax = ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.08, right=0.97,
                                    top=0.92, bottom=0.09)
        self._style_axes(ax)
        ax.set_title(f"Graphe de la fonction « {type_f} »",
                     color=COULEURS["texte"], fontsize=12)

        self.ligne, = ax.plot([], [], color=COULEURS["accent"],
                              linewidth=2.6, label=f"f(x) = {info['expr']}",
                              zorder=4)

        if info["asym_h"] is not None:
            ax.axhline(info["asym_h"], color="#8e8e93", linestyle="--",
                       linewidth=1.3,
                       label=f"asymptote y = {info['asym_h']:g}", zorder=3)
        if info["asym_v"] is not None:
            ax.axvline(info["asym_v"], color="#8e8e93", linestyle="--",
                       linewidth=1.3, label="asymptote x = 0", zorder=3)

        for kind, x, y in info["points"]:
            if not (np.isfinite(x) and np.isfinite(y)):
                continue
            col = COULEURS_POINTS[kind]
            ax.plot(x, y, "o", color=col, markersize=9,
                    markeredgecolor="white", zorder=6)
            if kind == "racine":
                lab = f"x = {x:.3g}"
            elif kind == "sommet":
                lab = f"S({x:.3g} ; {y:.3g})"
            else:
                lab = f"(0 ; {y:.3g})"
            ax.annotate(lab, (x, y), textcoords="offset points",
                        xytext=(8, 10), fontsize=9, color=col,
                        fontweight="bold", zorder=7)

        self.suivi, = ax.plot([], [], "o", color="#ff9800",
                              markersize=8, markeredgecolor="black", zorder=8)
        self.suivi_txt = ax.annotate(
            "", xy=(0, 0), xytext=(12, -22), textcoords="offset points",
            fontsize=10, zorder=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white",
                      ec="#999999", alpha=0.95))
        self.suivi.set_visible(False)
        self.suivi_txt.set_visible(False)

        ax.set_xlim(xlim)
        if ylim is None:
            self._ajuster_y()
        else:
            ax.set_ylim(ylim)

        self._maj_courbe()
        ax.callbacks.connect("xlim_changed", lambda _ax: self._maj_courbe())
        ax.legend(loc="upper left", fontsize=9, framealpha=0.9,
                  facecolor=COULEURS["panneau"], edgecolor=COULEURS["bordure"],
                  labelcolor=COULEURS["texte"])

    def _maj_courbe(self):
        if self.ligne is None:
            return
        x0, x1 = self.ax.get_xlim()
        marge = (x1 - x0) * 0.05
        x = np.linspace(x0 - marge, x1 + marge, 3000)
        self.ligne.set_data(
            x, self._evaluer(x, self._type_courant, self._c_courant))

    def _ajuster_y(self):
        x0, x1 = self.ax.get_xlim()
        x = np.linspace(x0, x1, 2000)
        y = self._evaluer(x, self._type_courant, self._c_courant)
        y = y[np.isfinite(y)]
        if y.size == 0:
            self.ax.set_ylim(-10, 10)
            return
        lo, hi = np.percentile(y, [2, 98])
        lo, hi = min(lo, 0.0), max(hi, 0.0)
        if hi - lo < 1e-9:
            lo, hi = lo - 1, hi + 1
        pad = (hi - lo) * 0.12
        self.ax.set_ylim(lo - pad, hi + pad)

    # ------------------------------------------------------------------
    def tracer(self, reinit=True, silent=False):
        c = self._get_coeffs(silent)
        if c is None:
            return
        type_f = self.type_fonction.get()

        if not reinit and self.affiche:
            xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        else:
            try:
                xmin = float(self.entry_xmin.get().replace(",", "."))
                xmax = float(self.entry_xmax.get().replace(",", "."))
            except ValueError:
                if not silent:
                    messagebox.showerror("Erreur", "Intervalle invalide.")
                return
            if xmin >= xmax:
                if not silent:
                    messagebox.showerror("Erreur", "x min doit être < x max.")
                return
            xlim, ylim = (xmin, xmax), None

        self._type_courant, self._c_courant = type_f, c
        self._pan = None
        info = self._analyser(type_f, c)
        self._construire_axes(type_f, c, info, xlim, ylim)
        self.affiche = True
        self._ecrire_resultat(info["texte"])
        self.toolbar.update()
        self.canvas.draw_idle()

    def ajuster_y(self):
        if not self.affiche:
            return
        self._ajuster_y()
        self.canvas.draw_idle()

    def effacer(self):
        self.affiche = False
        self.ligne = self.suivi = self.suivi_txt = None
        self._axes_vides()
        self._ecrire_resultat("")
        self.toolbar.update()
        self.canvas.draw_idle()

    # ------------------------------------------------------------------
    #  Interactions amin'le graphe
    # ------------------------------------------------------------------
    def _on_scroll(self, event):
        if not self.affiche or event.inaxes is not self.ax \
                or event.xdata is None:
            return
        f = 1 / 1.2 if event.button == "up" else 1.2
        xd, yd = event.xdata, event.ydata
        x0, x1 = self.ax.get_xlim()
        y0, y1 = self.ax.get_ylim()
        nx0, nx1 = xd - (xd - x0) * f, xd + (x1 - xd) * f
        ny0, ny1 = yd - (yd - y0) * f, yd + (y1 - yd) * f
        if 1e-9 < nx1 - nx0 < 1e9:
            self.ax.set_xlim(nx0, nx1)
        if 1e-9 < ny1 - ny0 < 1e9:
            self.ax.set_ylim(ny0, ny1)
        self.canvas.draw_idle()

    def _on_press(self, event):
        if not self.affiche or event.inaxes is not self.ax:
            return
        if event.dblclick:
            self.tracer(reinit=True)
            return
        if event.button != 1 or self.toolbar.mode != "":
            return
        self._pan = {"px": event.x, "py": event.y,
                     "xlim": self.ax.get_xlim(),
                     "ylim": self.ax.get_ylim()}
        self.canvas.get_tk_widget().config(cursor="fleur")

    def _on_release(self, event):
        self._pan = None
        self.canvas.get_tk_widget().config(cursor="")

    def _on_motion(self, event):
        if not self.affiche:
            return
        # Pan
        if self._pan is not None and event.x is not None:
            p = self._pan
            bbox = self.ax.bbox
            dx = (event.x - p["px"]) * (p["xlim"][1] - p["xlim"][0]) / bbox.width
            dy = (event.y - p["py"]) * (p["ylim"][1] - p["ylim"][0]) / bbox.height
            self.ax.set_xlim(p["xlim"][0] - dx, p["xlim"][1] - dx)
            self.ax.set_ylim(p["ylim"][0] - dy, p["ylim"][1] - dy)
            self.canvas.draw_idle()
            return

        # Suivi an'le point de curseur
        if event.inaxes is self.ax and event.xdata is not None \
                and self.suivi is not None:
            x = event.xdata
            y = float(self._evaluer(x, self._type_courant, self._c_courant))
            if np.isfinite(y):
                self.suivi.set_data([x], [y])
                self.suivi_txt.xy = (x, y)
                self.suivi_txt.set_text(f"({x:.3f} ; {y:.3f})")
                self.suivi.set_visible(True)
                self.suivi_txt.set_visible(True)
                self.status.config(text=f"x = {x:.4f}     f(x) = {y:.4f}")
            else:
                self.suivi.set_visible(False)
                self.suivi_txt.set_visible(False)
                self.status.config(text=f"x = {x:.4f}     f(x) non défini")
            self.canvas.draw_idle()
        elif self.suivi is not None and self.suivi.get_visible():
            self.suivi.set_visible(False)
            self.suivi_txt.set_visible(False)
            self.status.config(
                text="Molette : zoom  |  Clic gauche + glisser : déplacer  |  "
                     "Double-clic : réinitialiser")
            self.canvas.draw_idle()


class BarreOutilsAnalyse(NavigationToolbar2Tk):
    """Barre d'outils de l'onglet Analyse (Home = retrace)."""

    def __init__(self, canvas, parent, onglet):
        self.onglet = onglet
        super().__init__(canvas, parent, pack_toolbar=False)

    def home(self, *args):
        self.onglet.tracer(reinit=True)

    def set_message(self, s):
        pass


# ===========================================================================
#  FENÊTRE PRINCIPALE AN'LE APPLICATION
# ===========================================================================
class CalculatricePro(tk.Tk):
    """Fenêtre principale : contient les trois onglets et l'état partagé."""

    def __init__(self):
        super().__init__()
        self.title("Calculatrice Scientifique PRO")
        self.geometry("1320x860")
        self.minsize(1050, 720)
        self.configure(bg=COULEURS["fond"])

        # ------- État partagé an'le application -------
        self.degres = tk.BooleanVar(value=False)
        self.ans = 0.0

        self._configurer_style()

        # ------- karazana Onglets -------
        self.onglets = ttk.Notebook(self)
        self.onglets.pack(fill="both", expand=True, padx=4, pady=4)

        cadre_calc = ttk.Frame(self.onglets, style="Fond.TFrame")
        cadre_graph = ttk.Frame(self.onglets, style="Fond.TFrame")
        cadre_analyse = ttk.Frame(self.onglets, style="Fond.TFrame")

        self.onglets.add(cadre_calc, text="  🧮 Calculatrice  ")
        self.onglets.add(cadre_graph, text="  📈 Graphique  ")
        self.onglets.add(cadre_analyse, text="  🔬 Analyse  ")

        self.onglet_calculatrice = OngletCalculatrice(cadre_calc, self)
        self.onglet_calculatrice.pack(fill="both", expand=True)

        self.onglet_graphique = OngletGraphique(cadre_graph, self)
        self.onglet_graphique.pack(fill="both", expand=True)

        self.onglet_analyse = OngletAnalyse(cadre_analyse, self)
        self.onglet_analyse.pack(fill="both", expand=True)

        # ------- karazana Raccourcis -------
        # (Entrée est géré localement par chaque widget Entry.
        #  Échap : efface la calculatrice si on est sur son onglet)
        self.bind("<Escape>", self._on_escape)

        self.onglet_calculatrice.entry_expression.focus_set()

    # ------------------------------------------------------------------
    def _configurer_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Frames
        style.configure("Fond.TFrame", background=COULEURS["fond"])
        style.configure("Panneau.TFrame", background=COULEURS["panneau"])

        # Notebook
        style.configure("TNotebook", background=COULEURS["fond"],
                        borderwidth=0, tabmargins=[2, 4, 2, 0])
        style.configure("TNotebook.Tab", background=COULEURS["panneau"],
                        foreground=COULEURS["texte"],
                        padding=[22, 10], font=("Segoe UI", 11, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", COULEURS["accent"])],
                  foreground=[("selected", "#ffffff")])

        # Labels ahafahana mikitika an'le fonction
        style.configure("TLabel", background=COULEURS["fond"],
                        foreground=COULEURS["texte"], font=("Segoe UI", 10))
        style.configure("Gris.TLabel", background=COULEURS["fond"],
                        foreground=COULEURS["gris"], font=("Segoe UI", 10))
        style.configure("Titre.TLabel", background=COULEURS["fond"],
                        foreground=COULEURS["accent"],
                        font=("Segoe UI", 12, "bold"))

        # LabelFrame
        style.configure("TLabelframe", background=COULEURS["fond"],
                        foreground=COULEURS["texte"],
                        bordercolor=COULEURS["bordure"])
        style.configure("TLabelframe.Label", background=COULEURS["fond"],
                        foreground=COULEURS["accent"],
                        font=("Segoe UI", 10, "bold"))

        # Check / Radio ahafahana misafidy an'le application
        style.configure("TCheckbutton", background=COULEURS["fond"],
                        foreground=COULEURS["texte"])
        style.map("TCheckbutton",
                  background=[("active", COULEURS["fond"])],
                  foreground=[("active", COULEURS["accent"])])
        style.configure("TRadiobutton", background=COULEURS["fond"],
                        foreground=COULEURS["texte"])
        style.map("TRadiobutton",
                  background=[("active", COULEURS["fond"])],
                  foreground=[("active", COULEURS["accent"])])

        # Point d'entré
        style.configure("TEntry", fieldbackground=COULEURS["ecran"],
                        foreground=COULEURS["texte"],
                        insertcolor=COULEURS["texte"],
                        bordercolor=COULEURS["bordure"])
        style.configure("TSpinbox", fieldbackground=COULEURS["ecran"],
                        foreground=COULEURS["texte"],
                        insertcolor=COULEURS["texte"],
                        arrowcolor=COULEURS["gris"],
                        bordercolor=COULEURS["bordure"])

        # PanedWindow sy fenetre
        style.configure("TPanedwindow", background=COULEURS["fond"])
        style.configure("Sash", sashthickness=6,
                        gripcount=0, background=COULEURS["bordure"])

        # Scroll ao am'le application
        style.configure("Vertical.TScrollbar",
                        background=COULEURS["panneau"],
                        troughcolor=COULEURS["fond"],
                        bordercolor=COULEURS["fond"],
                        arrowcolor=COULEURS["gris"])

    # ------------------------------------------------------------------
    def basculer_mode(self):
        self.degres.set(not self.degres.get())
        # Actualisena ilay affichage
        self.onglet_calculatrice._maj_mode()
        # Rtraçage an'le courbe
        if self.onglet_graphique._expr_courante:
            self.onglet_graphique.tracer(reinit=False)
        if self.onglet_analyse.affiche:
            self.onglet_analyse.tracer(reinit=False, silent=True)

    def _on_escape(self, event=None):
        if self.onglets.index("current") == 0:
            self.onglet_calculatrice.effacer()


# ===========================================================================
if __name__ == "__main__":
    app = CalculatricePro()
    app.mainloop()