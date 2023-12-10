import { useState, FormEvent } from "react"
import { useHistory } from "react-router-dom"
import { useQueryClient } from "react-query"
import { useMutateAuth } from "./useMutateAuth"

export const useProcessAuth = () => {
  const history = useHistory()
  const queryClient = useQueryClient()
  const [email, setEmail] = useState('')
  const [pw, setPw] = useState('')
  const [isLogin, setLogin] = useState(true)
  const { loginMutation, registerMutation, logoutMutation } = useMutateAuth()
  const processAuth = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()  // 実行中はイベントが挿入されないようにする
    if (isLogin) {
      loginMutation.mutate({
        email: email,
        password: pw,
      })
    } else {
      // registerの場合は登録後そのままログイン処理を実行する
      await registerMutation
        .mutateAsync({
          email: email,
          password: pw,
        })
        .then(() =>
          loginMutation.mutate({
            email: email,
            password: pw
          })
        )
        .catch(() => {
            setPw('')
            setEmail('')
        })
    }
  }

  const logout = async () => {
    await logoutMutation.mutateAsync()
    // cookieに格納していたユーザー情報やタスク情報をクリアする
    queryClient.removeQueries('tasks')
    queryClient.removeQueries('user')
    queryClient.removeQueries('single')
    history.push('/')
  }
  return {
    email,
    setEmail,
    pw,
    setPw,
    isLogin,
    setLogin,
    processAuth,
    registerMutation,
    loginMutation,
    logout
  }
}
