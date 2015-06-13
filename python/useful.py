
# coding: utf-8

##### Plotting

# In[3]:

def remove_border(axes=None, top_ax=False, right_ax=False, left_ax=False, bottom_ax=False,
                  top_tick=False, right_tick=False, left_tick=False, bottom_tick=False):
    "Remove the border from a matplotlib plot"
    ax = axes or plt.gca()
    ax.spines['top'].set_visible(top_ax)
    ax.spines['right'].set_visible(right_ax)
    ax.spines['left'].set_visible(left_ax)
    ax.spines['bottom'].set_visible(bottom_ax)
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')
    if top_tick: ax.xaxis.tick_top()
    if bottom_tick: ax.xaxis.tick_bottom()
    if left_tick: ax.yaxis.tick_left()
    if right_tick: ax.yaxis.tick_right()
        
def to_percent(y, position):
    """Example usage: from matplotlib.ticker import FuncFormatter
    formatter = FuncFormatter(to_percent)
    ax.xaxis.set_major_formatter(formatter)"""
    import matplotlib as mpl
    s = str(int(100 * y))
    if mpl.rcParams['text.usetex'] == True: return s + r'$\%$'
    else: return s + '%'


##### Memory Usage

# In[4]:

def memory():
    import os
    from wmi import WMI
    w = WMI('.')
    result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
    return str(int(result[0].WorkingSet)/1E9) + ' GB' 


##### Code Conversion

# In[13]:

def exec_command(command_text):
    import subprocess
    p = subprocess.call(command_text, shell=True)
    if p == 1: raise Exception('failed command') 

def convert_to_py(fname, copy_to_anaconda):
    """This function converts an ipython notebook to a .py file, 
    removes the convert command, and copies the .py to the Anaconda
    directory where it can be imported by other notebooks.
    Don't forget to add '# end of .py file'."""
    exec_command("ipython nbconvert --to=python " + fname + ".ipynb")
    f = open(fname + '.py', 'r')
    all_lines = f.readlines()
    f.close()
    end_line_num = all_lines.index('# end of .py file\n')
    f = open(fname + '.py', 'w')
    f.writelines(all_lines[:end_line_num])
    f.close()
    if copy_to_anaconda:
        exec_command("cp " + fname + ".py /Users/stephenmcmurtry/anaconda/" + fname + ".py")


# In[14]:

