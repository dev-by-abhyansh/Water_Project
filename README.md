# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
 ## Steps to run this setup 
 1.firstly clone the repository in the folder 
 <br>
 <br>

 2.Create the python environment "conda create -p water_quality python=3.10 -y"
 <br>
 <br>

 3.Activate the environment "conda activate water_quality"
 <br>
 <br>

 4.requirements
   pip install pandas==2.1.4 numpy==1.26.4 scikit-learn==1.3.2 \
xgboost==1.7.6 shap==0.43.0 streamlit==1.32.0 \
matplotlib==3.8.3 seaborn==0.13.2 openpyxl==3.1.2 \
plotly==5.19.0 scipy==1.11.4 ipykernel==6.29.3 ipywidgets==8.1.2
<br>
<br>

5. Setup frontend
   cd frontend
npm install
<br>

6. Run the frontend
cd frontend
npm run dev
<br>

7.Install uvicorn
   pip install uvicorn
   <br><br>

8.create this file in the backend folder or in the root folder
   touch __init__.py
<br>

9.Install fastApi
    pip install fastapi uvicorn
    <br>

10.Install openpyxl
    pip install openpyxl
