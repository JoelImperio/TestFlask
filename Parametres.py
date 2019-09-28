import pandas as pd
import numpy as np
import os, os.path
path = os.path.dirname(os.path.abspath(__file__))
from Portefeuille import Portfolio


#Chargement des fichiers inputs contenant les hypothèses
h=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")
h1=pd.ExcelFile(path  + '/Hypotheses/TablesProphet 2018-12.xls').parse("Hypothèses")

#Importation d'une intance de Portfolio
p=Portfolio()

#Création de la class Hypothèse

class Hypo:
    
    __slot__=('un','vide','zero','run','shape')

    def __init__(self,hy=h,hy1=h1,MyShape=[],Run=[0,1,2,3,4,5], New=True):
        self.run=Run
        self.shape=MyShape
        self.un=np.ones(shape)
        self.vide=np.empty_like(self.un)
        self.zero=np.zeros_like(self.un)
        if New:
            self.h=hy
        else:
            self.h=hy1
        self.securityMarginMarge=1+self.h.iloc[53,2]
        self.securityMarginBio=1+self.h.iloc[54,2]
        self.inflation=1+self.h.iloc[55,2]

# Retourne une template formaté pour tous les runs    
    def templateAllrun(self):             
        myShape=self.shape
        myShape[2]=(p.shape)[2]
        result=np.zeros(myShape)
        return np.copy(result)
        

# Retourne une template avec les années chaque mois
    def templateAllYear(self):
        
        model=p.template
        model=model.copy()
        model.columns=model.columns.year
        return model.transpose()
    
# Retourne les frais de gestion par police
    def fraisGestion(self):
        
        fixfee=self.h.iloc[49,3]
        
        adminCost=self.templateAllrun()
        
        adminCost[:,:,:4]=fixfee
        adminCost[:,:,4]=fixfee*self.securityMarginMarge
        adminCost[:,:,5]=fixfee*self.securityMarginBio
        #Dimensionner pour les runs en appel    
        adminCost=adminCost[:,:,self.run] 
        
        return adminCost
    
    
    def fraisGestionPlacement(self):
        
        fixfee=self.h.iloc[50,3]

        investCost=self.templateAllrun()
        
        investCost[:,:,:4]=fixfee
        investCost[:,:,4]=fixfee*self.securityMarginMarge
        investCost[:,:,5]=fixfee*self.securityMarginBio
        #Dimensionner pour les runs en appel    
        investCost=investCost[:,:,self.run]
        
        return investCost
    
    def templateSinistrality(self,a):
        
        bestEstimate=self.h.iloc[a,3]
        bePlusMarge=self.h.iloc[a,4]
        bioEtFrais=self.h.iloc[a,5]

        sin=self.templateAllrun()
        
        sin[:,:,:4]=bestEstimate
        sin[:,:,4]=bePlusMarge
        sin[:,:,5]=bioEtFrais
        #Dimensionner pour les runs en appel    
        sin=sin[:,:,self.run]
        
        return sin

    def ipt(self):
        return self.templateSinistrality(14)
    def dcAccident(self):
        return self.templateSinistrality(15)
    def exo(self):
        return self.templateSinistrality(16)
    def itt(self):
        return self.templateSinistrality(17)
    def hospi(self):
        return self.templateSinistrality(18)
    def dc(self):
        return self.templateSinistrality(19)
    def fraisVisite(self):
        return self.templateSinistrality(20)
    
# Cette fonction retourne un vecteur avec les taux d'intérêt mensuel 
    def rate(self):
      
        rates=self.templateAllrun()       
        model=self.templateAllYear()
        model=model.iloc[:self.shape[1]]
        
        allrates=self.h.iloc[2:6,1:39].transpose()
        
        allrates=pd.merge(model,allrates, left_on=0,right_on=2,how='left')
        allrates=allrates.fillna(0)
        allrates=allrates.iloc[:,2:].to_numpy()
        
        #Conversion en taux mensuel
        allMensualrates=(1+allrates)**(1/12)-1
        allMensualrates=allMensualrates[np.newaxis,:,:]
        
        #Quel run pour quel courbe        
        runBE=[0,5,2,3]
        runRL=1
        runMG=4
        #Remplir la template pour chaque runs        
        rates[:,:,runBE]=allMensualrates[:,:,0,np.newaxis]
        rates[:,:,runMG]=allMensualrates[:,:,1]
        rates[:,:,runRL]=allMensualrates[:,:,2]
        #Dimensionner pour les runs en appel    
        rates=rates[:,:,self.run]
        
        return rates

# Taux de pd annuel pour chaque mois de projection   
    def pbRate(self):
        
        fixratePB=self.h.iloc[45,2]/100
        
        rate=self.rate()
        
        ratesPB=((1+rate)**12-1)-fixratePB
        
        return ratesPB

# Taux de rachat (anual rate) dimensionné pour les runs et polices   
    def lapse(self,policies):

 
        lapseSensiMoins=self.h.iloc[56,2]
        lapseSensiPlus=self.h.iloc[57,2]       
        cl=p.p['ClassPGGinit']
        
        lapseRates=self.h.iloc[23:32,1:12]
        lapseRates.columns = lapseRates.iloc[0]
        lapseRates=lapseRates.drop(lapseRates.index[0])
        lapseRates=lapseRates.set_index('Year').transpose()
        lapseRates=lapseRates[cl].transpose().to_numpy()
        lapseRates=lapseRates[:,:,np.newaxis,np.newaxis]

        dur=p.durationIf()
        

        condlist = [dur<12,dur<24,dur<36,dur<48,dur<60, 
                    dur<72,dur<84,dur<96,dur<108, 
                    dur>=108]
        choicelist = [lapseRates[:,0,:],lapseRates[:,1,:],lapseRates[:,2,:], 
                      lapseRates[:,3,:],lapseRates[:,4,:],lapseRates[:,5,:], 
                      lapseRates[:,6,:],lapseRates[:,7,:],lapseRates[:,8,:], 
                      lapseRates[:,9,:] ]
        mylapse=np.select(condlist, choicelist)

        
        mylapse[:,:,[3,5]]=mylapse[:,:,[3,5]]*lapseSensiMoins
        mylapse[:,:,2]=mylapse[:,:,2]*lapseSensiPlus
       
        
        sp=p.p.loc[p.p['PMBPOL'].isin(policies.p['PMBPOL'].values )]        
        pol=list(sp.index.values)
        
        #Dimensionner pour les runs et le portefeuille en appel    
        mylapse=np.take(mylapse, pol,axis=0)
        mylapse=mylapse[:,:,self.run]
        
        return mylapse

# Taux de réduction (anual rate) dimensionné pour les runs et polices  
    def reduction(self,policies):

# A vérifier si même sensibilité que rachat 
        lapseSensiMoins=self.h.iloc[56,2]
        lapseSensiPlus=self.h.iloc[57,2] 
        
        cl=p.p['ClassPGGinit']
        reductionRates=self.h.iloc[34:43,1:12]
        reductionRates.columns = reductionRates.iloc[0]
        reductionRates=reductionRates.drop(reductionRates.index[0])
        reductionRates=reductionRates.set_index('Year').transpose()
        reductionRates=reductionRates[cl].transpose().to_numpy()
        reductionRates=reductionRates[:,:,np.newaxis,np.newaxis]

        dur=p.durationIf()      
      

        condlist = [dur<12,dur<24,dur<36,dur<48,dur<60, 
                    dur<72,dur<84,dur<96,dur<108, 
                    dur>=108]
        choicelist = [reductionRates[:,0,:],reductionRates[:,1,:],reductionRates[:,2,:], 
                      reductionRates[:,3,:],reductionRates[:,4,:],reductionRates[:,5,:], 
                      reductionRates[:,6,:],reductionRates[:,7,:],reductionRates[:,8,:], 
                      reductionRates[:,9,:] ]
        myReduction=np.select(condlist, choicelist)

        
        myReduction[:,:,[3,5]]=myReduction[:,:,[3,5]]*lapseSensiMoins
        myReduction[:,:,2]=myReduction[:,:,2]*lapseSensiPlus
       
        
        sp=p.p.loc[p.p['PMBPOL'].isin(policies.p['PMBPOL'].values )]      
        pol=list(sp.index.values)
        
        #Dimensionner pour les runs et le portefeuille en appel    
        myReduction=np.take(myReduction, pol,axis=0)
        myReduction=myReduction[:,:,self.run]
        
        return myReduction

# Taux de commissions (anual rate) dimensionné pour les runs et polices (inclus les commissions de gestion)     
    def commissions(self,policies):
        
        cl=p.p['PMBMOD']
        
        commissionsRates=self.h.iloc[61:85,1:7]
        commissionsRates.columns = commissionsRates.iloc[0]
        commissionsRates=commissionsRates.drop(commissionsRates.index[0])
        commissionsRates=commissionsRates.set_index('Modalité').transpose()
        commissionsRates=commissionsRates[cl].transpose().to_numpy()
        commissionsRates=commissionsRates[:,:,np.newaxis,np.newaxis]
        
        dur=p.durationIf()      
      

        condlist = [dur<12,dur<24,dur<36, \
                    dur<48,dur>=48]
        
        choicelist = [commissionsRates[:,0,:],commissionsRates[:,1,:],commissionsRates[:,2,:], \
                      commissionsRates[:,3,:],commissionsRates[:,4,:]]
        
        myCommissions=np.select(condlist, choicelist)

        
        sp=p.p.loc[p.p['PMBPOL'].isin(policies.p['PMBPOL'].values )]      
        pol=list(sp.index.values)
        
        #Dimensionner pour les runs et le portefeuille en appel    
        myCommissions=np.take(myCommissions, pol,axis=0)
        myCommissions=myCommissions[:,:,self.run]
        
        return myCommissions

    


#####ICI pour faire des tests sur la class##########################################################

#myRun=[1,5]
myRun=[0,1,2,3,4,5]
policies=Portfolio(runs=myRun)
#policies.mod([8,9])
#policies.ids([2401101])

shape=policies.shape

hyp=Hypo(MyShape=shape, Run=myRun)

###Les fonctions de la class

a=hyp.fraisGestion()
b=hyp.fraisGestionPlacement()
c=hyp.rate()
d=hyp.pbRate()
e=hyp.lapse(policies)
f=hyp.ipt()
g=hyp.dcAccident()
h=hyp.exo()
i=hyp.itt()
j=hyp.hospi()
k=hyp.dc()
l=hyp.fraisVisite()
m=hyp.reduction(policies)
n=hyp.commissions(policies)








###Visualiser un vecteur np en réduisant une dimension
#data=n
#aa=pd.DataFrame(data[:,:,1])





