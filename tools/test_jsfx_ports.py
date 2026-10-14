"""Behavior/safety checks of delivered JSFX ports; not an EEL null test."""
from pathlib import Path
import tempfile
import subprocess
from test_ports import PRELUDE, port_class
from port_jsfx import NAMES
import re

def build():
    code=PRELUDE+'\n'.join(port_class(n) for n in NAMES)
    tests=[]
    for n in NAMES:
        params=re.findall(r'@param\([^\n]*\) (slider\w+) = ([^;]+);',Path('RNBO',n+'.txt').read_text())
        changes=''
        endpoint_assignments=[]
        for lo,hi,param in re.findall(r'@param\(\{ min: ([^,]+), max: ([^}]+) \}\) (slider\w+)',Path('RNBO',n+'.txt').read_text()):
            endpoint_assignments.append(f'p->{param} = mode==7 ? {lo} : {hi};')
        endpoints=''.join(endpoint_assignments)
        if 'GoldComp' in n: changes='p->slider5=-24;p->slider11=mode;p->slider16=150;p->slider20=3;p->slider21=2;'
        if 'Sky_is' in n: changes='p->slider6=.6;p->slider7=.5;p->slider10=12;p->slider51=mode%2;p->slider5=2;'
        if 'DubStep' in n: changes='p->sliderstep1=1;p->sliderstep17=1;p->sliderstep40=1;'
        if 'Filters' in n: changes='p->slider8=mode%4;p->slider2=mode%6;'
        tests.append(f'''
        for(double rate: {{44100.0,48000.0,96000.0}}) for(Int vector: {{1,64,256}}) for(int mode=0;mode<9;mode++) {{
            auto p=new Port_{n};p->sr=rate;p->vs=vector;
            {changes}
            if(mode>=7) {{ {endpoints} }}
            double energy=0;
            for(int t=0;t<65536;t++) {{
                p->in1=t<512 || t>32768 ? 0 : .7*sin(t*.03);
                p->in2=t<512 || t>32768 ? 0 : .4*cos(t*.021);
                p->in3=t*2.0/rate;p->run();
                if(!std::isfinite(p->out1)||!std::isfinite(p->out2)) {{std::cerr<<"{n} nonfinite rate "<<rate<<" mode "<<mode<<" sample "<<t<<"\\n";return 1;}}
                energy+=fabs(p->out1)+fabs(p->out2);
            }}
            if(mode<7 && energy<1e-10) throw std::runtime_error("{n}: no output");
            delete p;
        }}
        std::cout<<"PASS {n}: 81 rate/vector/control smoke cases including all-min/all-max\\n";
        ''')
    tests.append(r'''
    // Independent transposed-direct-form crossover equations from LR4 source.
    for(double rate: {44100.0,48000.0,96000.0}) for(int setting=0;setting<6;setting++) {
        auto p=new Port_mrelwood_HP_LP_LR4_Filters;p->sr=rate;p->slider8=3;p->slider2=setting;
        double state[2][2][7][2]{};
        int poles=setting+1, stages=poles==1?1:poles==2?2:poles==3?4:7;
        double reso=poles==1?-6:poles==2?-3:poles==3?-2.8:poles==4?-2.9:0;
        double fm=poles==3?1.24:poles==4?1.45:1;
        for(int t=0;t<4096;t++) {
            p->in1=sin(t*.091);p->in2=cos(t*.037);p->run();
            for(int hp=0;hp<2;hp++) for(int ch=0;ch<2;ch++) {
                // Source uses seven LP stages for >=4 but only four HP for 5/6.
                int count=hp && poles>=5 ? 4 : stages;
                double x=ch?p->in2:p->in1,w=2*PI*1000*(hp?1/fm:fm)/rate;
                double co=cos(w),alpha=sin(w)/(2*pow(2,reso/6));
                double b0=(1+(hp?co:-co))*.5/(1+alpha),b1=(hp?-2:2)*b0,b2=b0;
                double a1=-2*co/(1+alpha),a2=(1-alpha)/(1+alpha);
                for(int s=0;s<count;s++){double y=b0*x+state[hp][ch][s][0];state[hp][ch][s][0]=b1*x-a1*y+state[hp][ch][s][1];state[hp][ch][s][1]=b2*x-a2*y;x=y;}
                if(hp && (poles==1||poles==3||poles==4))x=-x;
                double actual=hp?(ch?p->out4:p->out3):(ch?p->out2:p->out1);
                if(fabs(x-actual)>1e-11)throw std::runtime_error("LR4 independent reference");
            }
        }
        delete p;
    }
    // Independent active GateIQ equations, including the source's squared gains.
    for(double rate: {44100.0,48000.0,96000.0}) {
        auto p=new Port_mrelwood_GateIQ;p->sr=rate;
        double lp[3]{},flt[4]{},c[4]{},g0[4]{},rc[4]{},reldura[4]{};
        double pole[3]={exp(-2*PI*1500/rate),exp(-2*PI*200/rate),exp(-2*PI*5000/rate)};
        double mult[4]={.05,.7,1.4,.55};
        for(int t=0;t<32768;t++){
            p->in1=t<512?0:.1*sin(t*.023);p->in2=t<512?0:.2*cos(t*.019);p->run();
            double mono=(p->in1+p->in2)*.5;
            lp[0]=(1-pole[0])*mono+pole[0]*lp[0];lp[1]=(1-pole[1])*lp[0]+pole[1]*lp[1];
            double hi=mono-lp[0];lp[2]=(1-pole[2])*hi+pole[2]*lp[2];
            double bands[4]={hi-lp[2],lp[2],lp[0]-lp[1],lp[1]},out=0;
            for(int b=0;b<4;b++){
                double ina=fabs(bands[b]),thr=pow(2,-45.0/6)*mult[b];
                if(ina>flt[b]){flt[b]+=(ina-flt[b])/11;c[b]=-300;}
                else {if(ina>flt[b]*.85)c[b]=std::min(0.0,c[b]);if(c[b]<1000)c[b]++;
                    flt[b]+=(ina-flt[b])*pow(std::min(1.0,std::max(0.0,c[b]/1000)+.01),3)*.01/(1+99*.15*.15);}
                if(flt[b]>thr){if(g0[b]<1)g0[b]+=.1/30;else g0[b]=1;rc[b]=reldura[b]=0;}
                else {rc[b]++;if(flt[b]<thr*.7 && reldura[b]==0)reldura[b]=rc[b]/(rate/10);
                    double tgt=std::min(1.0,std::max(0.0,flt[b]-thr*.35)/(thr-thr*.35));
                    g0[b]-=std::min((g0[b]-tgt)/(1+.15*.15*2*rate),1/(rate*.1));g0[b]=std::max(0.0,g0[b]);}
                double gain=1-pow(.5+.5*cos(g0[b]*3.14),2)*(1-pow(2,-20.0/6));out+=bands[b]*gain*gain;
            }
            if(fabs(out-p->out1)>1e-12)throw std::runtime_error("GateIQ independent reference");
        }delete p;
    }
    // Independent Wob-Wob one-button curve and cookbook LP recurrence.
    {
        auto p=new Port_mrelwood_DubStep_Wob_Wob;p->sliderstep1=1;
        double x1[2]{},x2[2]{},y1[2]{},y2[2]{};
        for(int t=0;t<32768;t++){
            p->in1=sin(t*.071);p->in2=cos(t*.023);p->in3=t*8.0/32768;p->run();
            double beat=p->in3-(1-sqrt(5.0/15))*.4;beat-=floor(beat/4)*4;
            double env=pow(std::max(0.0,1-beat*2)+std::max(0.0,beat*2-7),5);
            double w=2*3.14159265358*(20+1980*env)/44100,co=cos(w),al=sin(w)/1.4;
            double b0=(1-co)*.5/(1+al),b1=2*b0,a1=-2*co/(1+al),a2=(1-al)/(1+al);
            for(int ch=0;ch<2;ch++){double x=ch?p->in2:p->in1,y=b0*x+b1*x1[ch]+b0*x2[ch]-a1*y1[ch]-a2*y2[ch];x2[ch]=x1[ch];x1[ch]=x;y2[ch]=y1[ch];y1[ch]=y;
                if(fabs(y-(ch?p->out2:p->out1))>1e-11)throw std::runtime_error("Wob independent reference");}
        }delete p;
    }
    std::cout<<"PASS independent LR4 (18 configurations), GateIQ (3 rates), and Wob-Wob comparisons\n";
    {

        auto p=new Port_mrelwood_GateIQ;
        for(int i=0;i<4096;i++){p->in1=sin(i*.1);p->in2=cos(i*.03);p->run();if(p->out1!=p->out2)throw std::runtime_error("GateIQ active mono");}
        p->slider1=-96;p->frame=0;p->in1=.3;p->in2=-.2;p->run();
        if(p->out1!=.3||p->out2!=-.2)throw std::runtime_error("GateIQ bypass stereo");delete p;
    }
    {
        auto p=new Port_mrelwood_HP_LP_LR4_Filters;
        p->slider8=3;p->in1=1;p->in2=-.5;
        for(int i=0;i<100;i++)p->run();
        if(p->out3==0||p->out4==0)throw std::runtime_error("Crossover HP outlets");delete p;
    }
    // Rate changes and active automation must remain finite without resetting histories.
    for(int effect=0;effect<2;effect++) {
        if(effect==0){auto p=new Port_mrelwood_GoldComp4;
            for(int t=0;t<48000;t++){if(t==16000){p->slider5=-30;p->slider11=6;}if(t==32000){p->sr=96000;p->dspsetup();p->slider17=0;p->slider15=0;}
                p->in1=.2*sin(t*.03);p->in2=.1*cos(t*.09);p->run();if(!std::isfinite(p->out1))throw std::runtime_error("Gold automation");
                if(t>=32256 && fabs(p->out1-p->in1)>1e-12)throw std::runtime_error("Gold dry mix");}delete p;
        }else {auto p=new Port_mrelwood_Sky_is_the_limit_3v2_BETA;
            for(int t=0;t<48000;t++){if(t==16000){p->slider51=1;p->slider10=12;}if(t==32000){p->slider51=0;p->sr=96000;p->dspsetup();}
                p->in1=.2*sin(t*.03);p->in2=.1*cos(t*.09);p->run();if(!std::isfinite(p->out1))throw std::runtime_error("Sky automation");}delete p;}
    }
    {auto p=new Port_mrelwood_Chmahastic_Reverb_2;double tail=0;
        for(int t=0;t<96000;t++){if(t==48000)p->slider4=50;p->in1=t==512?.5:0;p->in2=0;p->run();if(t>4096)tail+=fabs(p->out1)+fabs(p->out2);}
        if(tail<1e-8)throw std::runtime_error("Chmahastic impulse tail");delete p;}
    std::cout<<"PASS routing, automation, sample-rate restart, Gold dry mix and Chmahastic impulse tail\n";
    ''')
    # C++ identifiers cannot contain the source filename's hyphens.
    code=code.replace('Port_mrelwood_DubStep_Wob-Wob','Port_mrelwood_DubStep_Wob_Wob').replace('Port_mrelwood_HP-LP_LR4_Filters','Port_mrelwood_HP_LP_LR4_Filters')
    main='int main(){try{'+''.join(tests)+'}catch(const std::exception& e){std::cerr<<e.what()<<"\\n";return 1;}return 0;}'
    main=main.replace('Port_mrelwood_DubStep_Wob-Wob','Port_mrelwood_DubStep_Wob_Wob').replace('Port_mrelwood_HP-LP_LR4_Filters','Port_mrelwood_HP_LP_LR4_Filters')
    return code+main

if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='rnbo-jsfx-') as tmp:
        src=Path(tmp,'tests.cpp');src.write_text(build());exe=Path(tmp,'tests')
        subprocess.run(['clang++','-std=c++17','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(src),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
