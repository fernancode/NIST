from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re


######## fluid types ########## 
def cas_registry():
    """
    Gets user input for the fluid and returns the CAS registry number

    """

    fluid_input = input("Enter fluid: ").lower()
    fluid = fluid_input.lower()
    
    if fluid == "methane":
        return "C74828", fluid
    elif fluid == "oxygen":
        return "C7782447", fluid
    elif fluid == "nitrogen":
        return "C7727379", fluid
    elif fluid == "hydrogen":
        return "C1333740", fluid
    elif fluid == "helium":
        return "C7440597", fluid


def plot_type():
    """
    Determine the plot type the user wants

    """

    plot_type = input("Plot type (Ts, Tv, Th, Tu): ")
    plot_type = plot_type.lower()

    # the temperature options
    if plot_type == "ts":
        x = 'Entropy (J/g*K)'
        y = 'Temperature (K)'
    elif plot_type == "th":
        x = 'Enthalpy (kJ/kg)'
        y = 'Temperature (K)'
    elif plot_type == "tv":
        x = 'Volume (m3/kg)'
        y = 'Temperature (K)'
    elif plot_type == "tu":
        x = 'Internal Energy (kJ/kg)'
        y = 'Temperature (K)'
    
    #the pressure options
    elif plot_type == "ps":
        x = 'Entropy (J/g*K)'
        y = 'Pressure (MPa)'
    elif plot_type == "ph":
        x = 'Enthalpy (kJ/kg)'
        y = 'Pressure (MPa)'
    elif plot_type == "pv":
        x = 'Volume (m3/kg)'
        y = 'Pressure (MPa)'
    elif plot_type == "pu":
        x = 'Internal Energy (kJ/kg)'
        y = 'Pressure (MPa)'

    else:
        x = 'Entropy (J/g*K)'
        y = 'Temperature (K)'
    return x, y


def plot_info(fluid_string):
    dark = input("Dark mode plot? (t/f): ")
    if dark.lower() == "t":
        dark = True
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
    else:
        dark = False
        fig, ax = plt.subplots()

    title_string = "Thermodynamic Properties " + fluid_string
    plt.title(title_string)
    return fig, ax, dark


def grid_stuff(dark, ax):
    if dark == True:
        ax.grid(b=True, which='major', color = 'w', linestyle = '--', alpha = .25)
        ax.grid(b=True, which='minor', color = 'w', linestyle = '--', alpha = .25)
    else:
        ax.grid(b=True, which='major', color = 'k', linestyle = '--', alpha = .1)
        ax.grid(b=True, which='minor', color = 'k', linestyle = '--', alpha = .1)


def legend_stuff(ax):
    blue = mpatches.Patch(color='tab:gray', label='Saturation')
    orange = mpatches.Patch(color='tab:red', label='Pressure (MPa)')
    #green = mpatches.Patch(color='tab:green', label='Property')
    red = mpatches.Patch(color='tab:blue', label='Density (kg/m^3)')
    purple = mpatches.Patch(color='tab:purple', label='Property')

    ax.get_legend().remove()
    ax.legend(handles=[blue, orange, red])


def get_dataframe(soup, datatype, rho=None):
    # "Supercritical"
    # "LiquidAndVapor"
    # "Vapor"
    # "Liquid"

    a = soup.find("h2",{"id":datatype})
    if a == None:
        return None
    table = a.find_next('table')
    df = pd.read_html(str(table))[0]
    
    if rho != None:
        if datatype == "Vapor":
            df = df[df['Density (kg/m3)'].isin([rho])]
    return df


def liquid_vapor_dome_temp(fluid, ax, x, y):
    """
    
    """
    
    #the url for accessing temperature saturation properties
    temp_inc_url = "https://webbook.nist.gov/cgi/fluid.cgi?ID="+fluid+"&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm&Type=SatP&RefState=DEF&Action=Page"

    #scrape this page to get the limits for temperature
    response = requests.get(temp_inc_url,headers={'user-agent':'Mozilla/5.0'})    
    soup = bs(response.text, "html.parser")        
    raw_max_string = soup.find('input',{'name':'THigh'}).find_next('td').string
    t_high= float(re.sub('[^0-9,.]','',raw_max_string))
    raw_low_string = soup.find('input',{'name':'TLow'}).find_next('td').string
    t_low= float(re.sub('[^0-9,.]','',raw_low_string))
    
    #scrape to get the table
    url = "https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=" + fluid + "&Type=SatP&Digits=5&THigh=" + str(t_high) + "&TLow=" + str(t_low) + "&TInc=1&RefState=DEF&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm"
    response = requests.get(url,headers={'user-agent':'Mozilla/5.0'})    
    soup = bs(response.text, "html.parser")
    df_liquid = get_dataframe(soup, "Liquid")
    df_vapor = get_dataframe(soup, "Vapor")

    #plot the tables given the dataframes
    df_liquid.plot(x=x, y=y ,ax=ax, legend=False, color='tab:gray')
    df_vapor.plot(x=x, y=y, ax=ax, legend=False, color='tab:gray')

    #grab the max density for later, subtract 1 to be safe
    rho_max = df_liquid.iloc[0]['Density (kg/m3)'] - 1
    return t_low, rho_max


def liquid_vapor_dome_pressure(fluid, ax, x, y):
    """

    """

    #the url for accessing temperature saturation properties
    pressure_inc_url = "https://webbook.nist.gov/cgi/fluid.cgi?ID="+fluid+"&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm&Type=SatT&RefState=DEF&Action=Page"

    #scrape this page to get the limits for pressure
    response = requests.get(pressure_inc_url,headers={'user-agent':'Mozilla/5.0'})    
    soup = bs(response.text, "html.parser")        
    raw_max_string = soup.find('input',{'name':'PHigh'}).find_next('td').string
    p_high= float(re.sub('[^0-9,.]','',raw_max_string))
    raw_low_string = soup.find('input',{'name':'PLow'}).find_next('td').string
    p_low= float(re.sub('[^0-9,.]','',raw_low_string))

    #scrape to get the table
    url = "https://webbook.nist.gov/cgi/fluid.cgi?PLow="+ str(p_low) + "&PHigh=" + str(p_high) + "&PInc=0.01&Applet=on&Digits=5&ID=C7727379&Action=Load&Type=SatT&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm&RefState=DEF"
    response = requests.get(url,headers={'user-agent':'Mozilla/5.0'})    
    soup = bs(response.text, "html.parser")
    df_liquid = get_dataframe(soup, "Liquid")
    df_vapor = get_dataframe(soup, "Vapor")

    #plot the tables
    df_liquid.plot(x=x, y=y ,ax=ax, legend=False, color='tab:gray')
    df_vapor.plot(x=x, y=y, ax=ax, legend=False, color='tab:gray')

    #grab the max density for later, subtract 1 to be safe
    rho_max = df_liquid.iloc[0]['Density (kg/m3)'] - 1
    return p_low, rho_max


def isobars(fluid, pressures, ax, t_low, t_high):
    """


    """
    #tlow needs to be greater than lowest saturation temp
    #t_high can be whatever

    for p in pressures:
        url = "https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=" + fluid + "&Type=IsoBar&Digits=5&P="+str(p)+"&THigh=" + str(t_high) + "&TLow=" + str(t_low) + "&TInc=1&RefState=DEF&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=Pa*s&STUnit=N%2Fm"
        response = requests.get(url,headers={'user-agent':'Mozilla/5.0'})    
        soup = bs(response.text, "html.parser")

        a = soup.find("h2",{"id":"Data"})
        #get the next table after the header
        try:
            isobar_table = a.find_next('table')
        except:
            pass
        #construct the table
        df_isobar = pd.read_html(str(isobar_table))[0]
        df_isobar.plot(x=x, y=y, color='tab:red', ax=ax)

        string = str(p)
        x_coor = df_isobar[x].iloc[-1]
        y_coor = df_isobar[y].iloc[-1]
        plt.annotate(string, (x_coor, y_coor), textcoords="offset points", xytext=(0,10), ha='center', color='tab:red')


def get_isobars():
    """
    get list of isobars that the user wants to plot

    """
    isobars = input("Isobars (MPa): ")
    isobars = isobars.replace(" ","")
    isobars = isobars.split(",")
    for index, x in enumerate(isobars):
        isobars[index] = float(x)
    return isobars


def isochors(fluid, rhos, ax, x, y, t_low, t_upper):
    """

    """

    for rho in rhos:
        url = "https://webbook.nist.gov/cgi/fluid.cgi?D=" + str(rho)  + "&TLow=" + str(t_low) + "&THigh=" + str(t_upper) + "&TInc=1&Digits=5&ID=" + fluid + "&Action=Load&Type=IsoChor&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm&RefState=DEF"
        response = requests.get(url,headers={'user-agent':'Mozilla/5.0'})    
        soup = bs(response.text, "html.parser")

        #### GET LIQUID VAPOR, VAPOR, AND SUPERCRITICAL TABLES
        dfs = []
        dfs.append(get_dataframe(soup, "Supercritical", rho))
        dfs.append(get_dataframe(soup, "LiquidAndVapor", rho))
        dfs.append(get_dataframe(soup, "Vapor", rho))
        for df in dfs:
            try:
                df.plot(x=x, y=y, ax=ax, legend=False, linestyle='--', color='tab:blue')
                string = str(rho)
                x_coor = df[x].iloc[-1]
                y_coor = df[y].iloc[-1]
                #if df.Phase.iloc[0] == 'vapor':
                a = plt.annotate(string, (x_coor, y_coor), textcoords="offset points", xytext=(-10,0), ha='center', color='tab:blue')
            except:
                pass


def get_isochors(rho_max):
    """
    get list of isobars that the user wants to plot

    """
    input_string = "Isochors (max "+str(rho_max)+ "kg/m^s): "
    isochors = input(input_string)
    isochors = isochors.replace(" ","")
    isochors = isochors.split(",")
    for index, x in enumerate(isochors):
        isochors[index] = float(x)
    return isochors



#print statements
print()
print("       Thermodynamic Property Plot Generator")
print("####################################################")
print("Webscrape NIST and generate constant property lines")
print("Enter desired constant property lines as comma \nseparated values, ex: 1, 2, 3")
print("####################################################")
print()

#get the fluid
fluid_cas, fluid_string = cas_registry()

#get the axes of the plot
x, y = plot_type()

#create the figure and axes, handle darkmode
fig, ax, dark = plot_info(fluid_string)

#create the liquid vapor dome
if y == "Temperature (K)":
    t_low, rho_max = liquid_vapor_dome_temp(fluid_cas, ax, x, y)

    t_upper = 320

    #get isobar list
    pressures = get_isobars()
    isobars(fluid_cas, pressures, ax, t_low, t_upper)    

    #get isochor list
    densitys = get_isochors(rho_max)
    isochors(fluid_cas, densitys, ax, x, y, t_low, t_upper)


elif y == "Pressure (MPa)":
    p_low, rho_max = liquid_vapor_dome_pressure(fluid_cas, ax, y, y)

    print("")


#handle legend things and labels
legend_stuff(ax)
ax.set_xlabel(x)
ax.set_ylabel(y)
grid_stuff(dark, ax)
plt.show()