def banner():
    # ANSI color codes
    RED = '\033[91m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    banner = f"""
{RED}:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:{END}
 {RED}.~!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!.{END} 
  {RED}.~!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!~.{END}  
    {RED}^!!!!!!!!^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^{END}    
     {RED}:!!!!!!!^     .....              ..{END}          
      {RED}.~!!!!!!~.  :P&&############&&&B57:{END}         
       {RED}.~!!!!!!!:  .5@@@@@@@@@@@@&BY!:  .:{END}        
         {RED}^!!!!!!!^   7&@@@@@@&GJ!:   .!5P^{END}        
          {RED}:!!!!!!!~   :^^^^^^.   .~JG&@G:{END}         
           {RED}.~!!!!!!~.        :!YG&@@@@Y{END}           
            {RED}.~!!!!!!!:      ?&@@@@@@@7{END}            
              {RED}^!!!!!!!.   .5@@@@@@@#~{END}        
               {RED}:!!!!!:   :B@@@@@@@G:{END}              
                {RED}.~!~.   !&@@@@@@@5.{END}               
                 {RED}.^    J@@@@@@@@J{END}                 
                     {RED}.P@@@@@@@&!{END}                  
                     {RED}7@@@@@@@B^{END}                   
                       {RED}7&@@@@P.{END}                    
                       {RED}~#@@Y{END}                      
                        {RED}:B?{END}                       
               {BLUE}https://crimson7.io{END}
            {BOLD}{WHITE}NPM Security Scanner v0.1.1{END}
"""
    print(banner)